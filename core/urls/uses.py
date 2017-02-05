from django.conf.urls import include, url
from core.views import use
urlpatterns = [
    url(r'^(?P<use_id>\d+)/$', use.UseDetail, name='use_detail'),
]
