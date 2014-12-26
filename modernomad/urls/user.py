from django.conf.urls import patterns, include, url
import registration.backends.default.urls
from core.views import Registration
from django.conf import settings
import core.forms

# Add the user registration and account management patters from the
# django-registration package, overriding the initial registration
# view to collect our additional user profile information.
urlpatterns = patterns('',
	url(r'^register/$', Registration.as_view(form_class = core.forms.UserProfileForm), name='registration_register'),
)

urlpatterns += patterns('core.views',
	url(r'^login/$', 'user_login', name='user_login'),
	url(r'^$', 'ListUsers', name='user_list'),
	url(r'^daterange/$', 'PeopleDaterangeQuery', name='people_daterange'),
	url(r'^(?P<username>(?!logout)(?!login)(?!register)[\w\d\-\.@+_]+)/$', 'GetUser', name='user_detail'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/edit/$', 'UserEdit', name='user_edit'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/addcard/$', 'UserAddCard', name='user_add_card'),
	url(r'^(?P<username>[\w\d\-\.@+_]+)/deletecard/$', 'UserDeleteCard', name='user_delete_card'),
)

urlpatterns += patterns('',
	url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', name="password_reset"),
	url(r'^password/done/$', 'django.contrib.auth.views.password_reset_done', name="password_reset_done"),
	url(r'^password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name="password_reset_confirm"),
	url(r'^password/complete/$', 'django.contrib.auth.views.password_reset_complete', name="password_reset_complete"),
)

# default patterns 
urlpatterns += registration.backends.default.urls.urlpatterns

# XXX can this be extracted and put into the gather app?
urlpatterns += url(r'^(?P<username>[\w\d\-\.@+_]+)/events/$', 'gather.views.user_events', name='user_events'),


