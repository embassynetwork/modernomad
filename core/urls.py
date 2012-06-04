# NOTE(mdh): This is different from the usual urls.py in that it
# doesn't define a top-level urlpatterns object.  The individual
# pattern sets here are intended to be used by a top-level pattern set
# elsewhere.

from django.conf.urls import patterns, include, url
import registration.backends.default.urls

user_patterns = patterns('core.views',
    url(r'^$', 'ListUsers'),
    url(r'^join/$', 'SignupUser'),
    url(r'^(?P<user_id>\d+)/$', 'GetUser'),
)

user_patterns += registration.backends.default.urls.urlpatterns

location_patterns = patterns('core.views',
    url(r'^$', 'ListLocations'),
)
