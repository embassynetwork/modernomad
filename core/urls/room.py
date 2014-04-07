from django.conf.urls import patterns, include, url

# /room patterns
urlpatterns = patterns('core.views',
	url(r'availability/$', 'CheckRoomAvailability', name='room_availability'),
)

