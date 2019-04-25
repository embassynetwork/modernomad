
import logging
from django.http import Http404
from django.shortcuts import render
from modernomad.core.models import Location

logger = logging.getLogger(__name__)


def location_detail(request, location_slug):
    try:
        location = (
            Location.objects
            .prefetch_related('house_admins', 'resources')
            .get(slug=location_slug)
        )
        logger.debug(location.get_members())
        logger.debug('--')
        logger.debug(request.user)

        if location.visibility == 'public' or location.visibility == 'link':
            has_permission = True
        elif request.user in location.get_members():
            has_permission = True
        else:
            has_permission = False

        if not has_permission:
            raise Location.DoesNotExist

    except Location.DoesNotExist:
        raise Http404("The location does not exist or you do not have permission to view it")

    return render(request, "location_detail.html", {'location': location, 'max_days': location.max_booking_days})
