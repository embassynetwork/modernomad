from django.conf.urls import patterns, include, url
from django.conf import settings
import registration.backends.default.urls

urlpatterns = patterns('',
	url(r'^create/$', 'gather.views.create_event', name='gather_create_event'),
	url(r'^upcoming/$', 'gather.views.upcoming_events', name='gather_upcoming_events'),
	url(r'^guide/$', 'gather.views.event_guide', name='gather_event_guide'),
	url(r'^past/$', 'gather.views.past_events', name='gather_past_events'),
	url(r'^review/$', 'gather.views.needs_review', name='gather_needs_review'),
	url(r'^message/$', 'gather.emails.event_message', name='gather_event_message'),
	url(r'^newuser/$', 'gather.views.new_user_email_signup', name='gather_new_user_email_signup'),
	url(r'^emailpreferences/(?P<username>[\w\d\-\.@+_]+)/$', 'gather.views.email_preferences', name='gather_email_preferences'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/edit/$', 'gather.views.edit_event', name='gather_edit_event'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/rsvp/yes/newuser/$', 'gather.views.rsvp_new_user', name='gather_rsvp_new_user'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/rsvp/no/$', 'gather.views.rsvp_cancel', name='gather_rsvp_cancel'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/rsvp/yes/$', 'gather.views.rsvp_event', name='gather_rsvp_event'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/endorse/$', 'gather.views.endorse', name='gather_event_endorse'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/publish/$', 'gather.views.event_publish', name='gather_event_publish'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/approve/$', 'gather.views.event_approve', name='gather_event_approve'),
	url(r'^(?P<event_id>\d+)/(?P<event_slug>[\w\d\-\.@+_]+)/$', 'gather.views.view_event', name='gather_view_event'),
)




