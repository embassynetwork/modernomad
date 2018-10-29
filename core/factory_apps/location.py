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

    name = factory.faker('street_name')
    slug = factory.faker('slug', provider='street_name')
    short_description = factory.faker('text')
    address = factory.faker('street_address')
    image = factory.django.ImageField(color='blue')
    profile_image = factory.django.ImageField(color='red')
    latitude = factory.faker('latitude')
    longitude = factory.faker('longitude')

    welcome_email_days_ahead = factory.faker('random_int')
    max_booking_days = factory.faker('random_int')

    stay_page = factory.faker('text')
    front_page_stay = factory.faker('text')
    front_page_participants = factory.faker('text')
    announcement = factory.faker('text')

    house_access_code = factory.faker('word')
    ssid = factory.faker('word')
    ssid_password = factory.faker('word')

    timezone = factory.faker('word')
    bank_account_number = factory.faker('random_int')
    routing_number = factory.faker('random_int')

    bank_name = factory.faker('word')
    name_on_account = factory.faker('word')
    email_subject_prefix = factory.faker('word')

    check_out = factory.faker('word')
    check_in = factory.faker('word')
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

    name = factory.faker('name')
    location = factory.SubFactory(LocationFactory)
    default_rate = factory.faker('pydecimal', left_digits=0, positive=True)
    description = factory.faker('text')
    summary = factory.faker('sentence')
    cancellation_policy = factory.faker('text')
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
    name = factory.faker('text')


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
    text_body = factory.faker('text')
    html_body = factory.faker('text')


class CapacityChangeFactory(factory.DjangoModelFactory):
    class Meta:
        model = CapacityChange

    created = factory.faker('past_datetime')
    resource = factory.SubFactory(ResourceFactory)
    start_date = factory.faker('future_date')
    quantity = factory.faker('pyint')
    accept_drft = factory.faker('pybool')


class LocationImageFactory(factory.DjangoModelFactory):
    pass


class RoomImageFactory(factory.DjangoModelFactory):
    pass


class BackingFactory(factory.DjangoModelFactory):
    pass
