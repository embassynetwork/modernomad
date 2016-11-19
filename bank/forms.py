from django import forms
from bank.models import Transaction, Entry, Account
from django.core.exceptions import ValidationError


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = '__all__'

