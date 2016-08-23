from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

import core.forms

# Add the user registration and account management patters from the
# django-registration package, overriding the initial registration
# view to collect our additional user profile information.
#urlpatterns = patterns('',
#	url(r'^register/$', Registration.as_view(form_class = core.forms.UserProfileForm), name='registration_register'),
#)

urlpatterns = patterns('core.views.unsorted',
	url(r'^$', 'ListUsers', name='user_list'),
	url(r'^login/$', 'user_login', name='user_login'),
	url(r'^check/email$', 'email_available', name='email_available'),
	url(r'^check/username$', 'username_available', name='username_available'),
	url(r'^register/$', 'register', name='registration_register'),
	url(r'^daterange/$', 'PeopleDaterangeQuery', name='people_daterange'),
	url(r'^(?P<username>(?!logout)(?!login)(?!register)(?!check)[\w\d\-\.@+_]+)/$', 'UserDetail', name='user_detail'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/avatar/$', 'UserAvatar', name='user_avatar'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/edit/$', 'UserEdit', name='user_edit'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/addcard/$', 'UserAddCard', name='user_add_card'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/deletecard/$', 'UserDeleteCard', name='user_delete_card'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/email/$', 'user_email_settings', name='user_email_settings'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/reservations/$', 'user_reservations', name='user_reservations'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/subscriptions/$', 'user_subscriptions', name='user_subscriptions'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/events/$', 'user_events', name='user_events'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/room/(?P<room_id>\d+)/$', 'user_edit_room', name='user_edit_room'),
)

urlpatterns += patterns('',
	url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', name="password_reset"),
	url(r'^password/done/$', 'django.contrib.auth.views.password_reset_done', name="password_reset_done"),
	url(r'^password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name="password_reset_confirm"),
	url(r'^password/complete/$', 'django.contrib.auth.views.password_reset_complete', name="password_reset_complete"),
)

# XXX can this be extracted and put into the gather app?
urlpatterns += url(r'^(?P<username>[\w\d\-\.@+_]+)/events/$', 'gather.views.user_events', name='user_events'),
