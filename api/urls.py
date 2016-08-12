from django.conf.urls import patterns, include, url

from api.views import *
from api.serializers import *

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
#router.register(r'users', UserViewSet)


urlpatterns = patterns('api.views',

	url(r'^', include(router.urls)),
	url(r'^availabilities/$', availabilities),
	url(r'^availability/(?P<availability_id>[0-9]+)/$', availability_detail),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^test/$', 'api_test', name='api_test'),
	url(r'user/(?P<username>[\w\d\-\.@+_]+)/current_location/occupancies.json$', CurrentLocationOccupancies.as_view(), name='current_location_occupancies'),
)
