from django.conf.urls import include, url
from django.contrib import admin
from modernomad import settings
from django.views.generic import RedirectView
import modernomad.views
import gather.views
import django.views
import jwt_auth.views
admin.autodiscover()

# media url hackery.
media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns = [
    url(r'^$', modernomad.views.index),
    url(r'^about/$', modernomad.views.about),
    url(r'^404/$', modernomad.views.ErrorView),
    url(r'^admin/', admin.site.urls),
    url(r'^people/', include('modernomad.urls.user')),
    url(r'^locations/', include('core.urls.location')),
    url(r'^events/emailpreferences/(?P<username>[\w\d\-\.@+_]+)/$', gather.views.email_preferences, name='gather_email_preferences'),
    url(r'^accounts/', include('bank.urls')),
    url(r'^drft/$', modernomad.views.drft),

    # various other useful things
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    url(r'^robots\.txt$', modernomad.views.robots),

    # api things
    url(r'^api-token-auth/', jwt_auth.views.obtain_jwt_token),
    url(r'^api/', include('api.urls')),
    url(r'^', include('graphapi.urls')),

    url(r'^%s/(?P<path>.*)$' % media_url, django.views.static.serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
]
