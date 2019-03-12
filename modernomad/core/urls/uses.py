from django.conf.urls import include, url
from modernomad.core.views.use import UseDetail

urlpatterns = [
    url(r'^(?P<use_id>\d+)/$', UseDetail, name='use_detail'),
    #url(r'^(?P<booking_id>\d+)/edit/$', BookingEdit, name='booking_edit'),
    #url(r'^(?P<booking_id>\d+)/delete/$', BookingDelete, name='booking_delete'),
    #url(r'^(?P<booking_id>\d+)/cancel/$', BookingCancel, name='booking_cancel'),
]
