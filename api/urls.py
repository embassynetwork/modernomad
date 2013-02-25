from django.conf.urls import patterns, include, url
from tastypie.api import Api

from api.resources import UsersResource, UserBaseResource, UpcomingResource


v1_api = Api(api_name='v1')
v1_api.register(UsersResource())
v1_api.register(UserBaseResource())
v1_api.register(UpcomingResource())


urlpatterns = patterns('',
    url(r'', include(v1_api.urls)),
)
