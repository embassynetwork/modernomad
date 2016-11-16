from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q, Sum

class Currency(models.Model):
    class Meta:
        verbose_name_plural = "Currencies"

    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=5)

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
    admins = models.ManyToManyField(User, related_name='accounts_administered', blank=True, help_text="May be blank")
    owner = models.ForeignKey(User, related_name='accounts_owned', null=True, blank=True, help_text="May be blank for group accounts")
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=32, choices=ACCOUNT_TYPES, default=STANDARD)

    def __unicode__(self):
        if self.owner:
            return "%s %s (%s)" % ( self.owner.first_name, self.owner.last_name, self.currency)
        elif self.type == Account.SYSTEM:
            # if a system account, is this a debit account or a credit account?
            if hasattr(self, 'systemaccount_credit'):
                return "%s SYSTEM CREDITS" % self.currency
            else:
                return "%s SYSTEM DEBITS" % self.currency
        else:
            return "No owner (%s)" % (self.currency)

    def get_total(self):
        # get all the entries for this account
        # add them up
        return self.entries.all().aggregate(
            total_amount = Sum('amount')
        )['total_amount']



class SystemAccount(models.Model):
    currency = models.OneToOneField(Currency)
    debits = models.OneToOneField(Account, related_name='systemaccount_debit')
    credits = models.OneToOneField(Account, related_name='systemaccount_credit')

@receiver(post_save, sender=Currency)
def currency_post_save(sender, instance, **kwargs):
    if not hasattr(instance, 'systemaccount'):
        credit_account = Account(currency=instance, type=Account.SYSTEM)
        credit_account.save()
        debit_account = Account(currency=instance, type=Account.SYSTEM)
        debit_account.save()
        SystemAccount.objects.create(currency=instance,debits=debit_account, credits=credit_account)

class Transaction(models.Model):
    reason = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    approver = models.ForeignKey(User, related_name="approved_transactions", blank=True, null=True)

class Entry(models.Model):
    account = models.ForeignKey(Account, related_name="entries")
    amount = models.IntegerField()
    transaction = models.ForeignKey(Transaction)
