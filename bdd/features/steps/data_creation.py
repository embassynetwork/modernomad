from behave import *
from core.factories import LocationFactory
from core.models import *

@given(u'there is a location called "{location_name}"')
def impl(context, location_name):
    LocationFactory.create(name = location_name).save()

@given(u'"{location_name}" has a room "{room_name}" with {bed_count:d} {beds} available')
def impl(context, location_name, room_name, bed_count, beds):
    location = Location.objects.get(name=location_name)
    room = Room(name=room_name, beds=bed_count, location=location,
        default_rate=100, shared=True, summary="blah")
    room.save()
    reservable = Reservable(start_date=datetime.date.today(), room=room)
    reservable.save()
    # assertEqual(room_name, False)
