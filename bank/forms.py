from django import forms
from bank.models import Transaction, Entry, Account
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'

def user_accounts():
    accounts = Account.objects.all()
    choices = []
    for a in accounts:
        choices.append((a.id, a.name))
    return choices
    #return request.user.profile.accounts_owned()

def recipient_accounts():
    accounts = Account.objects.all()
    choices = []
    for a in accounts:
        choices.append((a.id, a.name))
    return choices

class TransactionForm(forms.Form):
    reason = forms.CharField(label='Reason', max_length=200, required=True)
    from_account = forms.ChoiceField(required=True, choices=user_accounts)
    to_account = forms.ChoiceField(required=True, choices=recipient_accounts)
    amount = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
