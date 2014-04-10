from django.conf.urls import patterns, include, url

# urls starting in /reservation get sent here. 
urlpatterns = patterns('core.views',
	url(r'^create/$', 'ReservationSubmit', name='reservation_create'),
    url(r'^(?P<reservation_id>\d+)/$', 'ReservationDetail', name='reservation_detail'), 
	url(r'^(?P<reservation_id>\d+)/edit/$', 'ReservationEdit', name='reservation_edit'), 
    url(r'^(?P<reservation_id>\d+)/confirm/$', 'ReservationConfirm', name='reservation_confirm'), 
    url(r'^(?P<reservation_id>\d+)/delete/$', 'ReservationDelete', name='reservation_delete'), 
    url(r'^(?P<reservation_id>\d+)/cancel/$', 'ReservationCancel', name='reservation_cancel'), 

)



