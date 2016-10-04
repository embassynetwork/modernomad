from django.conf.urls import patterns, include, url

# urls starting in /booking get sent here.
urlpatterns = patterns(
    'core.views.unsorted',
    url(r'^(?P<booking_uuid>[0-9a-f\-]+)/payment/$', 'submit_payment', name='booking_payment'),
)

urlpatterns += patterns(
    'core.views.booking',
    url(r'^booking/submit$', 'BookingSubmit', name='booking_submit'),
    url(r'^(?P<booking_id>\d+)/$', 'BookingDetail', name='booking_detail'),
    url(r'^(?P<booking_id>\d+)/receipt/$', 'BookingReceipt', name='booking_receipt'),
    url(r'^(?P<booking_id>\d+)/edit/$', 'BookingEdit', name='booking_edit'),
    url(r'^(?P<booking_id>\d+)/confirm/$', 'BookingConfirm', name='booking_confirm'),
    url(r'^(?P<booking_id>\d+)/delete/$', 'BookingDelete', name='booking_delete'),
    url(r'^(?P<booking_id>\d+)/cancel/$', 'BookingCancel', name='booking_cancel'),
)
