from . import factory
from .location import LocationFactory

from gather.models import EventAdminGroup
from gather.models import EventSeries
from gather.models import Event
from gather.models import EventNotifications

from .user import UserFactory


class EventAdminGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = EventAdminGroup

    location = factory.SubFactory(LocationFactory)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.users.add(user)


class EventSeriesFactory(factory.DjangoModelFactory):
    class Meta:
        model = EventSeries

    name = factory.faker('word')
    description = factory.faker('paragraph')


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = Event

    created = factory.faker('past_datetime')
    updated = factory.faker('past_datetime')
    start = factory.faker('future_datetime')
    end = factory.faker('future_datetime')

    title = factory.faker('words')
    slug = factory.faker('words')

    description = factory.faker('paragraph')
    image = factory.django.ImageField(color='gray')

    notifications = factory.faker('pyboolean')

    where = factory.faker('city')
    creator = factory.SubFactory(UserFactory)

    organizer_notes = factory.faker('paragraph')

    limit = factory.faker('random_digit_or_empty')
    visibility = Event.PUBLIC
    status = Event.PENDING

    location = factory.SubFactory(LocationFactory)
    series = factory.SubFactory(EventSeriesFactory)
    admin = factory.SubFactory(EventAdminGroupFactory)

    @factory.post_generation
    def attendees(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for users in extracted:
                self.attendees.add(users)

    @factory.post_generation
    def organizers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for users in extracted:
                self.organizers.add(users)

    @factory.post_generation
    def endorsements(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for users in extracted:
                self.endorsements.add(users)


class EventNotificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = EventNotifications

    user = factory.SubFactory(UserFactory)
    reminders = factory.faker('pyboolean')

    @factory.post_generation
    def location_weekly(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for location in extracted:
                self.location_weekly.add(location)

    @factory.post_generation
    def location_publish(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for location in extracted:
                self.location_publish.add(location)
