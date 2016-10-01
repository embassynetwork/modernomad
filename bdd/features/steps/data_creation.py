from behave import *
from core.factories import LocationFactory
from core.models import *


@given(u'there is a location called "{location_name}"')
def impl(context, location_name):
    LocationFactory(name=location_name, slug='someloc')


@given(u'"{location_name}" has a room "{room_name}" with {bed_count:d} {beds} available')
def impl(context, location_name, room_name, bed_count, beds):
    location = Location.objects.get(name=location_name)
    room = Resource(name=room_name, location=location, default_rate=100, summary="blah")
    room.save()
    Availability(start_date=datetime.date.today(), resource=room, quantity=1).save()
