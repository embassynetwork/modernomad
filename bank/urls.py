from django.conf.urls import patterns, include, url
from bank.views import *
from bank.views import AccountDetail, AccountList

urlpatterns = [
    url(r'^(?P<account_id>\d+)/$', AccountDetail.as_view(), name='account_detail'),
    url(r'^list/$', AccountList.as_view(), name='account_list'),
]


