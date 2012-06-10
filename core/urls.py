# NOTE(mdh): This is different from the usual urls.py in that it
# doesn't define a top-level urlpatterns object.  The individual
# pattern sets here are intended to be used by a top-level pattern set
# elsewhere.

from django.conf.urls import patterns, include, url
import registration.backends.default.urls

import core.forms

user_patterns = patterns('core.views',
    url(r'^$', 'ListUsers', name='user_list'),
    url(r'^(?P<user_id>\d+)/$', 'GetUser', name='user_details'),
)

# Add the user registration and account management patters from the
# django-registration package, overriding the initial registration
# view to collect our additional user profile information.
user_patterns += patterns('',
    url(r'^register/$', 'registration.views.register',
        {'backend': 'core.views.RegistrationBackend',
         'form_class': core.forms.CombinedUserForm},
        name='registration_register'),
)
user_patterns += registration.backends.default.urls.urlpatterns

house_patterns = patterns('core.views',
    url(r'^$', 'ListHouses', name='house_list'),
    url(r'^(?P<house_id>\d+)/$', 'GetHouse', name='house_details'),
)
