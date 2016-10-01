from django.conf.urls import patterns, include, url

from api.views.availabilities import *
from rest_framework import routers


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

urlpatterns = patterns(
    'api.views',
    url(r'^', include(router.urls)),
    url(r'^availabilities/$', availabilities),
    url(r'^availability/(?P<availability_id>[0-9]+)$', availability_detail),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
