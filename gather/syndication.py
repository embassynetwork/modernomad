from django_ical.views import ICalFeed
from django.core.urlresolvers import reverse
from gather.models import Event
from modernomad.core.models import Location
from django.shortcuts import get_object_or_404

class PublicEventsFeed(ICalFeed):
    product_id = '-//embassynetwork.com//events'
    timezone = 'PST'
    file_name = "events.ics"

    def get_object(self, request, location_slug):
        return get_object_or_404(Location, slug=location_slug)

    def items(self, obj):
        rv = Location.objects.get(slug="redvic")
        return Event.objects.filter(location=obj).filter(status=Event.LIVE).filter(visibility=Event.PUBLIC).order_by('-start')

    def item_title(self, obj):
        return obj.title

    def item_description(self, obj):
        return obj.description

    def item_start_datetime(self, obj):
        return obj.start

    def item_end_datetime(self, obj):
        return obj.end

    def item_link(self, obj):
        return reverse('gather_view_event', args=[obj.location.slug, obj.pk, obj.slug])

