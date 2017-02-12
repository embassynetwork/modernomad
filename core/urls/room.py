from django.conf.urls import include, url
from core.views import unsorted
from core.views import resource_availability

# /room patterns
urlpatterns = [
    url(r'(?P<room_id>\d+)/htmlcal/?year=(?P<year>\d+)&month=(?P<month>\d+)$$', unsorted.room_cal_request, name='room_cal_request'),
    url(r'(?P<room_id>\d+)/htmlcal/$', unsorted.room_cal_request, name='room_cal_request'),
    url(r'availability/$', resource_availability.CheckRoomAvailability, name='room_availability'),
]
