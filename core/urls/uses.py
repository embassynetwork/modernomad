from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'core.views.use',
    url(r'^(?P<use_id>\d+)/$', 'UseDetail', name='use_detail'),
    #url(r'^(?P<booking_id>\d+)/edit/$', 'BookingEdit', name='booking_edit'),
    #url(r'^(?P<booking_id>\d+)/delete/$', 'BookingDelete', name='booking_delete'),
    #url(r'^(?P<booking_id>\d+)/cancel/$', 'BookingCancel', name='booking_cancel'),
)
