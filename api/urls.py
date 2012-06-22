from django.conf.urls import patterns, include, url
from tastypie.api import Api

from api.resources import HousesResource, ResourcesResource, UsersResource, EndorsementsResource, LocationsResource


v1_api = Api(api_name='v1')
v1_api.register(HousesResource())
v1_api.register(ResourcesResource())
v1_api.register(UsersResource())
v1_api.register(EndorsementsResource())
v1_api.register(LocationsResource())

urlpatterns = patterns('',
    url(r'', include(v1_api.urls)),
)
