from faker import Faker
from fakers.providers import lorem
from fakers.providers import profile
from fakers.providers import address
from faker.providers import BaseProvider
import factory
from core.models import Location
from core.models import Resource
from core.models import LocationFee
from core.models import Fee

factory.Faker.add_provider(lorem)
factory.Faker.add_provider(profile)
factory.Faker.add_provider(address)


class Provider(BaseProvider):
    # Note that the class name _must_ be ``Provider``.
    def slug(self, provider):
        fake = Faker()
        value = getattr(fake, provider)()
        return value.replace(' ', '-')


factory.Faker.add_provider(Provider)


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
    default_rate = factory.faker('random_int')
    description = factory.faker('text')
    summary = factory.faker('sentence')
    cancellation_policy = factory.faker('text')
    image = factory.django.ImageField(color='green')
