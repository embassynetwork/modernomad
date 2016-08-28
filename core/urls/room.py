from django.conf.urls import patterns, include, url

# /room patterns
urlpatterns = patterns(
    'core.views',
    url(r'^list/$', 'unsorted.guest_rooms', name='location_rooms'),
    url(r'(?P<room_id>\d+)/$', 'unsorted.view_room', name='view_room'),
    url(r'(?P<room_id>\d+)/htmlcal/?year=(?P<year>\d+)&month=(?P<month>\d+)$$', 'unsorted.room_cal_request', name='room_cal_request'),
    url(r'(?P<room_id>\d+)/htmlcal/$', 'unsorted.room_cal_request', name='room_cal_request'),
    url(r'availability/$', 'resource_availability.CheckRoomAvailability', name='room_availability'),
)
