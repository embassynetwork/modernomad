from django import forms
from bank.models import Transaction, Entry, Account, Currency
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.db.models import Q


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'

def user_accounts(user):
    #accounts = Account.objects.all()
    accounts = user.profile.accounts_in_currency(Currency.objects.get(name='DRFT'))
    choices = [("", "---------")]
    for a in accounts:
        choices.append((a.id, a.name))
    return choices

def recipient_accounts():
    #user_accounts = Account.objects.all()
    account_list = user.profile.accounts_in_currency(Currency.objects.get(name='DRFT'))
    accounts = Account.objects.all()
    for a in accounts:
        if a.primary_for.all():
            account_list.append(a)
    choices = [("", "---------")]
    for a in account_list:
        choices.append((a.id, a.name))
    return choices

class TransactionForm(forms.Form):
    from_account = forms.ModelChoiceField(required=True, queryset=None)
    to_account = forms.ModelChoiceField(required=True, queryset=None)
    reason = forms.CharField(label='Reason', max_length=200, required=True)
    amount = forms.IntegerField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        accounts = Account.objects.filter(currency=Currency.objects.get(name="DRFT")).filter(Q(owners=user.pk) | Q(admins=user.pk))
        self.fields['from_account'].queryset = accounts
        self.fields['to_account'].queryset = accounts
        for field_name, field in self.fields.items():
            if field_name == 'from_account' or field_name == 'to_account':
                field.widget.attrs['class'] = 'form-control chosen-select'
            else:
                field.widget.attrs['class'] = 'form-control'
