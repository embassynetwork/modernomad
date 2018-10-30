from django.contrib.flatpages.models import FlatPage

from core.models import Location
from core.models import Resource
from core.models import LocationFee
from core.models import LocationMenu
from core.models import LocationFlatPage
from core.models import LocationEmailTemplate
from core.models import CapacityChange
from .booking import FeeFactory
from . import factory


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker('street_name')
    slug = factory.Faker('slug', provider='street_name')
    short_description = factory.Faker('text')
    address = factory.Faker('street_address')
    image = factory.django.ImageField(color='blue')
    profile_image = factory.django.ImageField(color='red')
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')

    welcome_email_days_ahead = factory.Faker('random_int')
    max_booking_days = factory.Faker('random_int')

    stay_page = factory.Faker('text')
    front_page_stay = factory.Faker('text')
    front_page_participants = factory.Faker('text')
    announcement = factory.Faker('text')

    house_access_code = factory.Faker('word')
    ssid = factory.Faker('word')
    ssid_password = factory.Faker('word')

    timezone = factory.Faker('word')
    bank_account_number = factory.Faker('random_int')
    routing_number = factory.Faker('random_int')

    bank_name = factory.Faker('word')
    name_on_account = factory.Faker('word')
    email_subject_prefix = factory.Faker('word')

    check_out = factory.Faker('word')
    check_in = factory.Faker('word')
    visibility = factory.Iterator(['public', 'members', 'link'])

    @factory.post_generation
    def house_admins(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.house_admins.add(user)

    @factory.post_generation
    def readonly_admins(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.readonly_admins.add(user)


class ResourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Resource

    name = factory.Faker('name')
    location = factory.SubFactory(LocationFactory)
    default_rate = factory.Faker('pydecimal', left_digits=0, positive=True)
    description = factory.Faker('text')
    summary = factory.Faker('sentence')
    cancellation_policy = factory.Faker('text')
    image = factory.django.ImageField(color='green')


class LocationFeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationFee

    location = factory.SubFactory(LocationFactory)
    fee = factory.SubFactory(FeeFactory)


class LocationMenuFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationMenu

    location = factory.SubFactory(LocationFactory)
    name = factory.Faker('text')


class FlatpageFactory(factory.DjangoModelFactory):
    class Meta:
        model = FlatPage


class LocationFlatPageFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationFlatPage

    menu = factory.SubFactory(LocationMenuFactory)
    flatpage = factory.SubFactory(FlatpageFactory)


class LocationEmailTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationEmailTemplate

    location = factory.SubFactory(LocationFactory)
    key = 'admin_daily_update'
    text_body = factory.Faker('text')
    html_body = factory.Faker('text')


class CapacityChangeFactory(factory.DjangoModelFactory):
    class Meta:
        model = CapacityChange

    created = factory.Faker('past_datetime')
    resource = factory.SubFactory(ResourceFactory)
    start_date = factory.Faker('future_date')
    quantity = factory.Faker('pyint')
    accept_drft = factory.Faker('pybool')


class LocationImageFactory(factory.DjangoModelFactory):
    pass


class RoomImageFactory(factory.DjangoModelFactory):
    pass


class BackingFactory(factory.DjangoModelFactory):
    pass
