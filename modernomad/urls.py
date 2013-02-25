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
	url(r'^payment/$', 'modernomad.views.payment'),
	url(r'^thanks/$', 'modernomad.views.thanks'),
#	url(r'^dashboard/$', 'core.views.dashboard'),
	
	
	url(r'^events/$', 'modernomad.views.events'),
	url(r'^404/$', 'modernomad.views.ErrorView'),


	# The core views, broken out into a couple of top-level paths.
	url(r'^people/', include(core.urls.user_patterns)),
	url(r'^locations/', include(core.urls.house_patterns)),
	url(r'^reservation/', include(core.urls.reservation_patterns)),

	# The modernomad API.
	url(r'^api/', include('api.urls')),

	# The Django admin interface.
	url(r'^admin/', include(admin.site.urls)),
)

# media url hackery. 
urlpatterns += patterns('',
	(r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
	 { 'document_root': settings.MEDIA_ROOT, 'show_indexes':True }),
)

