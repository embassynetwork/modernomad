from django.conf.urls import patterns, include, url
from django.contrib import admin
from modernomad.urls import user
from modernomad import settings
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'modernomad.views.index'),
	url(r'^about/$', 'modernomad.views.about'),
	url(r'^stay/$', 'modernomad.views.stay'),
	url(r'^404/$', 'modernomad.views.ErrorView'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^people/', include('modernomad.urls.user')),
	url(r'^locations/', include('core.urls.location')),
	url(r'^events/$', 'gather.views.upcoming_events_all_locations'),
	url(r'^events/emailpreferences/(?P<username>[\w\d\-\.@+_]+)/$', 'gather.views.email_preferences', name='gather_email_preferences'),

	# various other useful things
	url(r'^ico/favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
)

# media url hackery. 
media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns += patterns('',
	(r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
	 { 'document_root': settings.MEDIA_ROOT, 'show_indexes':True }),
)


