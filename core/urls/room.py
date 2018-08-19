from django.conf.urls import patterns, include, url
from core.views.unsorted import guest_rooms, view_room, room_cal_request
from core.views import resource_availability

# /room patterns
urlpatterns = [
    url(r'^list/$', guest_rooms, name='location_rooms'),
    url(r'(?P<room_id>\d+)/$', view_room, name='view_room'),
    url(r'(?P<room_id>\d+)/htmlcal/?year=(?P<year>\d+)&month=(?P<month>\d+)$$', room_cal_request, name='room_cal_request'),
    url(r'(?P<room_id>\d+)/htmlcal/$', room_cal_request, name='room_cal_request'),
    url(r'availability/$', resource_availability.CheckRoomAvailability, name='room_availability'),
]
