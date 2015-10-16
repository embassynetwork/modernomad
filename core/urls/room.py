from django.conf.urls import patterns, include, url

# /room patterns
urlpatterns = patterns('core.views',
	url(r'^list/$', 'guest_rooms', name='location_rooms'),
	url(r'(?P<room_id>\d+)/$', 'view_room', name='view_room'),	
	url(r'(?P<room_id>\d+)/htmlcal$', 'room_cal_request', name='room_cal_request'),	
	url(r'availability/$', 'CheckRoomAvailability', name='room_availability'),
  
)

