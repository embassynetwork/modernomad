from django.conf.urls import include, url

from modernomad.core.views.booking import *
from modernomad.core.views.unsorted import submit_payment

# urls starting in /booking get sent here.
urlpatterns = [
    url(r'^(?P<booking_uuid>[0-9a-f\-]+)/payment/$', submit_payment, name='booking_payment'),
]

urlpatterns += [
    url(r'^submit$', BookingSubmit, name='booking_submit'),
    url(r'^(?P<booking_id>\d+)/$', BookingDetail, name='booking_detail'),
    url(r'^(?P<booking_id>\d+)/receipt/$', BookingReceipt, name='booking_receipt'),
    url(r'^(?P<booking_id>\d+)/edit/$', BookingEdit, name='booking_edit'),
    url(r'^(?P<booking_id>\d+)/confirm/$', BookingConfirm, name='booking_confirm'),
    url(r'^(?P<booking_id>\d+)/delete/$', BookingDelete, name='booking_delete'),
    url(r'^(?P<booking_id>\d+)/cancel/$', BookingCancel, name='booking_cancel'),
]
