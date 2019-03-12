from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from modernomad.core.views.unsorted import ListUsers, user_login, email_available, username_available, register, PeopleDaterangeQuery, UserDetail, UserAvatar, UserEdit, UserAddCard, UserDeleteCard, user_email_settings, user_subscriptions, user_events, user_edit_room
from modernomad.core.views.booking import UserBookings
from modernomad.core.views.redirects import old_user_bookings_redirect
from django.contrib.auth.views import *
import gather.views

import modernomad.core.forms

# Add the user registration and account management patters from the
# django-registration package, overriding the initial registration
# view to collect our additional user profile information.
# urlpatterns = patterns('',
#    url(r'^register/$', Registration.as_view(form_class = core.forms.UserProfileForm), name='registration_register'),
# )

urlpatterns = [
    url(r'^$', ListUsers, name='user_list'),
    url(r'^login/$', user_login, name='user_login'),
    url(r'^check/email$', email_available, name='email_available'),
    url(r'^check/username$', username_available, name='username_available'),
    url(r'^register/$', register, name='registration_register'),
    url(r'^daterange/$', PeopleDaterangeQuery, name='people_daterange'),
    url(r'^(?P<username>(?!logout)(?!login)(?!register)(?!check)[\w\d\-\.@+_]+)/$', UserDetail, name='user_detail'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/avatar/$', UserAvatar, name='user_avatar'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/edit/$', UserEdit, name='user_edit'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/addcard/$', UserAddCard, name='user_add_card'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/deletecard/$', UserDeleteCard, name='user_delete_card'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/email/$', user_email_settings, name='user_email_settings'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/subscriptions/$', user_subscriptions, name='user_subscriptions'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/events/$', user_events, name='user_events'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/room/(?P<room_id>\d+)/$', user_edit_room, name='user_edit_room'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/bookings/$', UserBookings, name='user_bookings'),
    # gracefully handle old urls
    url(r'^(?P<username>[\w\d\-\.@+_]+)/reservations/$', old_user_bookings_redirect),
    url(r'^logout/$', logout_then_login),
    url(r'^password/reset/$', password_reset, name="password_reset"),
    url(r'^password/done/$', password_reset_done, name="password_reset_done"),
    url(r'^password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm, name="password_reset_confirm"),
    url(r'^password/complete/$', password_reset_complete, name="password_reset_complete"),
]

# XXX can this be extracted and put into the gather app?
# TODO name collision with user_events above.
urlpatterns += url(r'^(?P<username>[\w\d\-\.@+_]+)/events/$', gather.views.user_events, name='user_events'),
