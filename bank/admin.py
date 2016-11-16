from django.contrib import admin
from bank.models import *

# Register your models here.
class EntryInline(admin.StackedInline):
    model = Entry
    extra = 2

class AccountAdmin(admin.ModelAdmin):
    model = Account
    raw_id_fields = ("owner", "admins")
    list_filter = ('type',)
    list_display = ('__unicode__', 'type')

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    inlines = [EntryInline,]
    raw_id_fields = ("approver",)

class SystemAccountInline(admin.StackedInline):
    model = SystemAccount
    readonly_fields = ('debits', 'credits')

class CurrencyAdmin(admin.ModelAdmin):
    model = Currency
    inlines = [SystemAccountInline,]


admin.site.register(Account, AccountAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Transaction, TransactionAdmin)

