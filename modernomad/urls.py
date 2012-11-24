from django.conf.urls import patterns, include, url
from django.contrib import admin

import core.urls #import reservation_patterns
import settings

admin.autodiscover()

media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns = patterns('',
    url(r'^$', 'modernomad.views.index'),
    url(r'^about/$', 'modernomad.views.about'),
    url(r'^residents/$', 'modernomad.views.residents'),
    url(r'^stay/$', 'modernomad.views.stay'),
    url(r'^upcoming/$', 'modernomad.views.upcoming'),
    url(r'^upcoming-timeline/$', 'modernomad.views.upcomingTimeline'),
    url(r'^guestinfo/$', 'modernomad.views.GuestInfo'),
    
    
    url(r'^events/$', 'modernomad.views.events'),
    url(r'^submitpayment/$', 'modernomad.views.submitpayment'),
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

# media url hackery. TODO does new-django have a better way to do this?
urlpatterns += patterns('',
    (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
     { 'document_root': settings.MEDIA_ROOT, 'show_indexes':True }),
)

