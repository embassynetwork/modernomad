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

class AccountAdmin(admin.ModelAdmin):
    model = Account
    raw_id_fields = ("owner", "admins")
    list_filter = ('type',)
    list_display = ('__unicode__', 'get_balance', 'account_admins', 'type')
    inlines = [EntryReadOnlyInline,]

    def account_admins(self, obj):
        return ", ".join(["%s %s" % (a.first_name, a.last_name) for a in obj.admins.all()])

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    inlines = [EntryInline,]
    raw_id_fields = ("approver",)
    save_as = True
    readonly_fields = ('valid',)

class SystemAccountInline(admin.StackedInline):
    model = SystemAccount
    readonly_fields = ('debits', 'credits')

class CurrencyAdmin(admin.ModelAdmin):
    model = Currency
    inlines = [SystemAccountInline,]


admin.site.register(Account, AccountAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Transaction, TransactionAdmin)

