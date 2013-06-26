from django.conf.urls import patterns, include, url
from django.contrib import admin

import core.urls #import reservation_patterns
import settings

admin.autodiscover()

media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns = patterns('',
	url(r'^$', 'modernomad.views.index'),
	url(r'^about/$', 'modernomad.views.about'),
	url(r'^community/$', 'modernomad.views.community'),
	url(r'^stay/$', 'modernomad.views.stay'),
	url(r'^occupancy/$', 'modernomad.views.occupancy'),
	url(r'^calendar/$', 'modernomad.views.calendar'),
	url(r'^guestinfo/$', 'modernomad.views.GuestInfo'),
	url(r'^participate/$', 'modernomad.views.participate'),
	url(r'^payment/$', 'modernomad.views.GenericPayment'),
	url(r'^thanks/$', 'modernomad.views.thanks'),
	url(r'^today/$', 'modernomad.views.today'),
	
#	url(r'^dashboard/$', 'core.views.dashboard'),
	
	
	url(r'^events/$', 'modernomad.views.events'),
	url(r'^404/$', 'modernomad.views.ErrorView'),


	# The core views, broken out into a couple of top-level paths.
	url(r'^people/', include(core.urls.user_patterns)),
	url(r'^locations/', include(core.urls.house_patterns)),
	url(r'^reservation/', include(core.urls.reservation_patterns)),
	url(r'^manage/', include(core.urls.management_patterns)),
	url(r'^room/', include(core.urls.room_patterns)),

	# The modernomad API.
	url(r'^api/', include('api.urls')),

	# The Django admin interface.
	url(r'^admin/', include(admin.site.urls)),

	# various other useful things
	url(r'^ico/favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/media/img/favicon.ico'}),
)

# media url hackery. 
urlpatterns += patterns('',
	(r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
	 { 'document_root': settings.MEDIA_ROOT, 'show_indexes':True }),
)

