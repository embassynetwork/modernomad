from django.conf.urls import patterns, include, url
from tastypie.api import Api
from wc_profiles.api import HouseResource, ResourceResource, UserResource, EndorsementResource

v1_api = Api(api_name='v1')
v1_api.register(HouseResource())
v1_api.register(ResourceResource())
v1_api.register(UserResource())
v1_api.register(EndorsementResource())

urlpatterns = patterns('',
    url(r'', include(v1_api.urls)),
)
