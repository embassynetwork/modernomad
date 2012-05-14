from django.conf.urls import patterns, include, url

urlpatterns = patterns('wc_profiles.views',
	url(r'^$', 'index'),
	url(r'^join/$', 'signup'),
	url(r'^locations/$', 'locations'),
	url(r'^(?P<user_id>\d+)/$', 'user'),
)


