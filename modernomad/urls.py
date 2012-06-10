from django.conf.urls import patterns, include, url
from django.contrib import admin

import core.urls
import settings

admin.autodiscover()

media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns = patterns('',
    url(r'^$', 'modernomad.views.index'),
    url(r'^about/$', 'modernomad.views.about'),
    url(r'^community/$', 'modernomad.views.community'),
    url(r'^membership/$', 'modernomad.views.membership'),

    # The core views, broken out into a couple of top-level paths.
    url(r'^members/', include(core.urls.user_patterns)),
    url(r'^locations/', include(core.urls.house_patterns)),

    # The modernomad API.
    url(r'^api/', include('api.urls')),

    # The Django admin interface.
    url(r'^admin/', include(admin.site.urls)),
)

# media url hackery. TODO does new-django have a better way to do this?
urlpatterns += patterns('',
    (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
     { 'document_root': settings.MEDIA_ROOT }),
)

