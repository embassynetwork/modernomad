from django.conf.urls import patterns, include, url

# /room patterns
urlpatterns = patterns('core.views',
	url(r'^list/$', 'guest_rooms', name='location_rooms'),
	url(r'(?P<room_id>\d+)/$', 'view_room', name='view_room'),	
	url(r'availability/$', 'CheckRoomAvailability', name='room_availability'),
)

