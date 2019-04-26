import pytz

from . import factory
from .location import LocationFactory

from gather.models import EventAdminGroup
from gather.models import EventSeries
from gather.models import Event
from gather.models import EventNotifications

from .user import UserFactory, SuperUserFactory


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
        else:
            self.users.add(SuperUserFactory())


class EventSeriesFactory(factory.DjangoModelFactory):
    class Meta:
        model = EventSeries

    name = factory.Faker('word')
    description = factory.Faker('paragraph')


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = Event

    created = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    updated = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    start = factory.Faker('future_datetime', tzinfo=pytz.UTC)
    end = factory.Faker('future_datetime', tzinfo=pytz.UTC)

    title = factory.Faker('word')
    slug = factory.Faker('word')

    description = factory.Faker('paragraph')
    image = factory.django.ImageField(color='gray')

    notifications = factory.Faker('pybool')

    where = factory.Faker('city')
    creator = factory.SubFactory(UserFactory)

    organizer_notes = factory.Faker('paragraph')

    limit = factory.Faker('random_digit')
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
    reminders = factory.Faker('pybool')

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
