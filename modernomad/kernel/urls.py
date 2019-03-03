from django.conf.urls import url, include
from .apps import app_name  # noqa
from . import views


location_patterns = [
    url(r'^$', views.location, name='location_detail'),
]

urlpatterns = [
    url(r'^(?P<location_slug>[\w-]+)/', include(location_patterns)),
]
