from django.conf.urls import patterns, include, url

from api.views.capacities import *
from rest_framework import routers


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

urlpatterns = patterns(
    'api.views',
    url(r'^', include(router.urls)),
    url(r'^capacities/$', capacities),
    url(r'^capacity/(?P<capacity_id>[0-9]+)$', capacity_detail),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
