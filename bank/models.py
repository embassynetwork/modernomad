from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q, Sum
from django.utils import timezone
from django.db.models.functions import Coalesce

class Currency(models.Model):
    name = models.CharField(max_length=200, unique=True)
    symbol = models.CharField(max_length=5, unique=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __unicode__(self):
        return self.name

class Account(models.Model):
    SYSTEM = 'system'
    STANDARD = 'standard'

    ACCOUNT_TYPES = (
            # first value stored in db, second value is what is shown to user
            (SYSTEM, 'System'),
            (STANDARD, 'Standard'),
        )
    currency = models.ForeignKey(Currency, related_name="accounts")
    admins = models.ManyToManyField(User, verbose_name="Admins (optional)", related_name='accounts_administered', blank=True, help_text="May be blank")
    owners = models.ManyToManyField(User, related_name='accounts_owned', blank=True, help_text="May be blank for group accounts")
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=32, choices=ACCOUNT_TYPES, default=STANDARD)

    def __unicode__(self):
        if self.name:
            return self.name + " (%s)" % (self.currency)
        if self.owners.all():
            owner_list = ", ".join(["%s %s" % (o.first_name, o.last_name) for o in self.owners.all()])
            return owner_list + " (%s)" % (self.currency)
        elif self.type == Account.SYSTEM:
            # if a system account, is this a debit account or a credit account?
            if hasattr(self, 'systemaccount_credit'):
                return "%s SYSTEM CREDITS" % self.currency
            else:
                return "%s SYSTEM DEBITS" % self.currency
        else:
            return "No owner (%s)" % (self.currency)

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

class SystemAccount(models.Model):
    currency = models.OneToOneField(Currency)
    debits = models.OneToOneField(Account, related_name='systemaccount_debit')
    credits = models.OneToOneField(Account, related_name='systemaccount_credit')

@receiver(post_save, sender=Currency)
def currency_post_save(sender, instance, **kwargs):
    ''' JKS this needs to be post save because the currency object needs to
    exist in the database for the accounts to link to it'''
    if not hasattr(instance, 'systemaccount'):
        credit_account = Account(currency=instance, type=Account.SYSTEM)
        credit_account.save()
        debit_account = Account(currency=instance, type=Account.SYSTEM)
        debit_account.save()
        SystemAccount.objects.create(currency=instance,debits=debit_account, credits=credit_account)

class Transaction(models.Model):
    reason = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(default=timezone.now)
    approver = models.ForeignKey(User, related_name="approved_transactions", blank=True, null=True)
    valid = models.BooleanField(default=False)

    def __unicode__(self):
        return "Transaction %s" % self.pk

    def save(self, *args, **kwargs):
        # We can check validity through checking if the balance is 0, OR if any
        # of the entries are invalid... seems redundant (possibilities for
        # incongruency?) but I think we want the 'valid' flag on entry as well
        # as on transaction, for easy filtering. 
        validity_requirements_met = False
        entries = self.entries.all()

        # check that all entries balance out
        balance = sum([e.amount for e in entries])
        if len(entries) > 1 and balance == 0:
            validity_requirements_met = True
        else:
            validity_requirements_met = False

        # only need to make the second check if the first passes
        if validity_requirements_met == True:
            # check that all entries are between accounts of the same type
            if len(set([e.account.currency for e in entries])) > 1:
                validity_requirements_met = False
            else:
                validity_requirements_met = True

        if validity_requirements_met == True:
            self.valid = True
            Entry.objects.filter(transaction=self).update(valid=True)
        else:
            self.valid = False
            Entry.objects.filter(transaction=self).update(valid=False)

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
    valid = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Entries"
        ordering=['transaction__date']

    def __unicode__(self):
        return "Entry: account %s for %d" % (self.account, self.amount)

    def save(self, *args, **kwargs):
        # save the entry first so that we can validate any changes (since we're
        # pulling them from the DB)
        super(Entry, self).save(*args, **kwargs)
        if self.transaction:
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
            print self.transaction.entries.all()
            other_entry = self.transaction.entries.exclude(id=self.id).first()
            return other_entry.account
        else:
            print 'Warning! found invalid transaction id=%d' % self.transaction.id
            print self.transaction.entries.all()
            return None

    def balance_at(self):
        return self.account.balance_at_entry(self)

''' check that transaction entries sum to 0
    that the spending user will have an allowable balance after the transaction is completed. 
    that the correct permissions are in place for both accounts
    transfer only between accounts of the same currency
    if entry is updated, update transaction: if entry is valid, then transaction is valid. 
'''
