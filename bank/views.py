from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from bank.models import *
from django.db.models import Q

# Create your views here.
class AccountDetail(View):
    template_name = 'accounts_detail.html'

    def get(self, request, account_id):
        account = Account.objects.get(id=account_id)
        # ensure user has permissions
        assert (request.user in account.owners.all()
                or
                request.user in account.admins.all()
            )
        return render(request, self.template_name, {'account': account})

class AccountList(View):
    template_name = 'accounts_list.html'
    def get(self, request):
        accounts = Account.objects.filter(Q(owners=request.user) | Q(admins=request.user)).order_by('currency')
        print accounts
        return render(request, self.template_name, {'accounts': accounts})
