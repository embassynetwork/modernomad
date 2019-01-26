from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models import Q, Sum
from django.utils import timezone
from django.db.models.functions import Coalesce
import logging
logger = logging.getLogger(__name__)

class Currency(models.Model):
    name = models.CharField(max_length=200, unique=True)
    symbol = models.CharField(max_length=5, unique=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Currency, self).save(*args, **kwargs)
        if not hasattr(self, 'systemaccounts'):
            credit_account = Account.objects.create(currency=self, name="%s SYSTEM CREDIT" % self.name, type = Account.CREDIT)
            debit_account = Account.objects.create(currency=self, name="%s SYSTEM DEBIT" % self.name, type = Account.DEBIT)
            SystemAccounts.objects.create(currency=self, credit=credit_account, debit=debit_account)

class Account(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    ACCOUNT_TYPES = (
            # first value stored in db, second value is what is shown to user
            (CREDIT, 'Credit'),
            (DEBIT, 'Debit'),
        )

    currency = models.ForeignKey(Currency, related_name="accounts")
    admins = models.ManyToManyField(User, verbose_name="Admins (optional)",
            related_name='accounts_administered', blank=True, help_text="May be blank"
        )
    owners = models.ManyToManyField(User, related_name='accounts_owned',
            blank=True, help_text="May be blank for group accounts"
        )
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=32, choices=ACCOUNT_TYPES, default=CREDIT,
            help_text="A credit (expense, asset) account always has a balance > 0. A debit (revenue, liability) account always has a balance < 0. #helpfulnothelpful."
        )

    def __str__(self):
        return self.name + " (%s)" % (self.currency)

    def is_credit(self):
        return (self.type == Account.CREDIT)

    def is_debit(self):
        return (self.type == Account.DEBIT)

    def get_balance(self):
        # sum all valid entries for this account
        return self.entries.filter(valid=True).aggregate(
            total_amount = Coalesce(Sum('amount'), 0)
        )['total_amount']

    def balance_at_entry(self, entry):
        # return the balance of the account after the entry was recorded
        return self.entries.filter(valid=True).filter(
            transaction__date__lte=entry.transaction.date).aggregate(
            total_amount = Coalesce(Sum('amount'), 0)
        )['total_amount']

    def owner_names(self):
        return [o.first_name for o in self.owners.all()]


class SystemAccounts(models.Model):
    # money coming into or out of the system (either due to real transfers or
    # minting) is recorded in these accounts.
    currency = models.OneToOneField(Currency)
    credit = models.OneToOneField(Account, related_name="+")
    debit = models.OneToOneField(Account, related_name="+")


class Transaction(models.Model):
    reason = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(default=timezone.now)
    approver = models.ForeignKey(User, related_name="approved_transactions", blank=True, null=True)
    valid = models.BooleanField(default=False)

    def __str__(self):
        return "Transaction %s" % self.pk

    def save(self, *args, **kwargs):
        entries = self.entries.all()
        if len(entries) < 2:
            # this is a fresh transaction, or only the first entry
            self.valid = False

        else: # only if there are 2 transactions
            if len(entries) != 2:
                # the transaction object needs to be saved first without *any*
                # entries before the entries can themselves link to the transaction
                # as a foreign key.
                raise Exception("Transactions must have 2 entries")

            # check that all entries balance out
            balance = sum([e.amount for e in entries])
            if balance != 0:
                # Note that this effectively prevents us from editing a
                # transaction as well, since one entry will get updated before
                # the other, and cause this error.
                raise Exception("Transaction entries must balance out and there must be only 2")

            # check that all entries are between accounts of the same type
            if len(set([e.account.currency for e in entries])) > 1:
                raise Exception("Transaction entries must be between accounts of the same currency")

            self.valid = True
            # call update instead of save() so we don't end up in an infinite
            # loop of save()'s calling each other.
            Entry.objects.filter(transaction=self).update(valid=True)

        super(Transaction, self).save(*args, **kwargs)

    def magnitude(self):
        # the magnitude value of a transaction is the total amount it sums to
        # in either the positive or negative direction. It's required to be
        # symmetric, so we just pick one direction to sum over.
        resp = self.entries.filter(amount__gt=0).aggregate(Sum('amount'))
        return resp['amount__sum']

class Entry(models.Model):
    account = models.ForeignKey(Account, related_name="entries")
    amount = models.IntegerField()
    transaction = models.ForeignKey(Transaction, related_name="entries")
    # a transaction will always be invalid until it is linked to a second one
    # through a transaction. because the objects get saved in serial, we can't
    # avoid a temporary invalid state.
    valid = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Entries"
        ordering=['-transaction__date']

    def __str__(self):
        return "Entry: account %s for %d" % (self.account, self.amount)

    def save(self, *args, **kwargs):
        # save the entry first so that we can validate any changes (since we're
        # pulling them from the DB)
        super(Entry, self).save(*args, **kwargs)
        #if self.transaction:
        entries = self.transaction.entries.all()
        balance = sum([e.amount for e in entries])
        if balance == 0:
            Entry.objects.filter(transaction=self.transaction).update(valid=True)
        else:
            Entry.objects.filter(transaction=self.transaction).update(valid=False)
        self.transaction.save()

    def with_account(self):
        if self.valid:
            # what account was this transaction _from_?
            other_entry = self.transaction.entries.exclude(id=self.id).first()
            return other_entry.account
        else:
            logger.debug('Warning! found invalid transaction id=%d' % self.transaction.id)
            return None

    def balance_at(self):
        return self.account.balance_at_entry(self)

@receiver(pre_save, sender=Entry)
def entry_pre_save(sender, instance, **kwargs):
    # enforce hard balance limits for debit and credit accounts.
    current_balance = instance.account.get_balance()
    if instance.account.is_debit() and (current_balance + instance.amount > 0):
        raise Exception("Error: insufficient balance for transaction. Debit account %d must retain a balance less than 0." % instance.account.id)
    elif instance.account.is_credit() and (current_balance + instance.amount < 0):
        raise Exception("Error: insufficient balance for transaction. Credit account %d must retain a balance greater than 0." % instance.account.id)



''' check that transaction entries sum to 0
    that the spending user will have an allowable balance after the transaction is completed.
    that the correct permissions are in place for both accounts
    transfer only between accounts of the same currency
    if entry is updated, update transaction: if entry is valid, then transaction is valid.
'''
