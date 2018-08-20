from django.conf.urls import include, url

from rest_framework import routers
from api.views.capacities import capacities, capacity_detail
import rest_framework.urls

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^capacities/$', capacities),
    url(r'^capacity/(?P<capacity_id>[0-9]+)$', capacity_detail),
    url(r'^api-auth/', include(rest_framework.urls, namespace='rest_framework')),
]
