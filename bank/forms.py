from django import forms
from bank.models import Transaction, Entry, Account
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.db.models import Q


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'

def user_accounts(user):
    #accounts = Account.objects.all()
    accounts = user.profile.accounts()
    choices = []
    for a in accounts:
        choices.append((a.id, a.name))
    return choices

def recipient_accounts():
    accounts = Account.objects.all()
    choices = []
    for a in accounts:
        choices.append((a.id, a.name))
    return choices

class TransactionForm(forms.Form):
    reason = forms.CharField(label='Reason', max_length=200, required=True)
    from_account = forms.ModelChoiceField(required=True, queryset=None)
    to_account = forms.ModelChoiceField(required=True, queryset=None)
    amount = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        accounts = Account.objects.filter(Q(owners=user.pk) | Q(admins=user.pk)) 
        self.fields['from_account'].queryset = accounts 
        self.fields['to_account'].queryset = accounts 


    
