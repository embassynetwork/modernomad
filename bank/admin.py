from django.contrib import admin
from bank.models import *
from bank.forms import TransactionForm

class EntryReadOnlyInline(admin.TabularInline):
    model = Entry
    extra = 0
    readonly_fields = ('valid','amount', 'transaction')
    can_delete = False
    
class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0
    readonly_fields = ('valid',)

class SystemAccountsInline(admin.TabularInline):
    model = SystemAccounts
    readonly_fields = ('credit', 'debit')
    can_delete = False

class AccountAdmin(admin.ModelAdmin):
    model = Account
    raw_id_fields = ("owners", "admins")
    list_filter = ('type', 'owners')
    list_display = ('__str__', 'balance', 'account_owners', 'account_admins', 'type')
    inlines = [EntryReadOnlyInline,]

    def balance(self, obj):
        return obj.get_balance()

    def account_owners(self, obj):
        return ", ".join(["%s %s" % (a.first_name, a.last_name) for a in obj.owners.all()])

    def account_admins(self, obj):
        return ", ".join(["%s %s" % (a.first_name, a.last_name) for a in obj.admins.all()])

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    inlines = [EntryInline,]
    raw_id_fields = ("approver",)
    save_as = True
    readonly_fields = ('valid',)

class CurrencyAdmin(admin.ModelAdmin):
    model = Currency
    inlines = [SystemAccountsInline,]


admin.site.register(Account, AccountAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Transaction, TransactionAdmin)

