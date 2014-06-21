from django.conf.urls import patterns, include, url

per_location_patterns = [
    url(r'^$', 'core.views.location', name='location_home'),
	url(r'^about/$', 'core.views.about', name='location_about'),
	url(r'^residents/$', 'core.views.residents', name='location_residents'),
	url(r'^stay/$', 'core.views.stay', name='location_stay'),
	url(r'^occupancy/$', 'core.views.occupancy', name='location_occupancy'),
	url(r'^calendar/$', 'core.views.calendar', name='location_calendar'),
	url(r'^payment/$', 'core.views.GenericPayment', name='location_payment'),
	url(r'^thanks/$', 'core.views.thanks', name='location_thanks'),
	url(r'^today/$', 'core.views.today', name='location_today'),
	url(r'^email/current$', 'core.emails.current', name='location_email_current'),
	url(r'^email/stay$', 'core.emails.stay', name='location_email_stay'),

	url(r'^events/', include('gather.urls')),

	url(r'^reservation/', include('core.urls.reservations')),
	url(r'^manage/', include('core.urls.manage')),
	url(r'^room/', include('core.urls.room')),
]

urlpatterns = patterns('core.views',
	url(r'^$', 'location_list', name='location_list'),
	url(r'^(?P<location_slug>\w+)/', include(per_location_patterns)),
)


