from django.conf.urls import patterns, include, url

from api.views import *

urlpatterns = patterns('api.views',
	url(r'^test/$', 'api_test', name='api_test'),	
	url(r'user/(?P<username>[\w\d\-\.@+_]+)/current_location/occupancies.json$', CurrentLocationOccupancies.as_view(), name='current_location_occupancies'),	
)
