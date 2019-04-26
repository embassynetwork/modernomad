
import logging

from django.http import Http404
from django.views.generic import DetailView
from rules.contrib.views import PermissionRequiredMixin

from modernomad.core.models import Location

logger = logging.getLogger(__name__)


class LocationDetail(PermissionRequiredMixin, DetailView):
    model = Location
    context_object_name = 'location'
    template_name = 'location/location_detail.html'
    permission_required = 'location.can_view'
    slug_url_kwarg = 'location_slug'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('house_admins', 'resources')
        return qs

    def handle_no_permission(self):
        raise Http404("The location does not exist or you do not have permission to view it")
