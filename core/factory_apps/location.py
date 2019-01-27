from django.contrib.flatpages.models import FlatPage

from core.models import Location
from core.models import Resource
from core.models import LocationFee
from core.models import LocationMenu
from core.models import LocationFlatPage
from core.models import LocationEmailTemplate
from core.models import CapacityChange
from core.models import Fee
from . import factory


class FeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Fee

    description = factory.Faker('text', max_nb_chars=100)
    percentage = factory.Faker('pyfloat', left_digits=0, positive=True)
    paid_by_house = factory.Faker('pybool')


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location
        django_get_or_create = ('slug',)

    name = factory.Faker('street_name')
    slug = factory.Faker('slug', name='street_name')
    short_description = factory.Faker('text')
    address = factory.Faker('street_address')
    image = factory.django.ImageField(color='blue', width=800, height=225)
    profile_image = factory.django.ImageField(color='red', width=336, height=344)
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')

    welcome_email_days_ahead = factory.Iterator([1,2,3,4,5])
    max_booking_days = factory.Iterator([1,5,14,30])

    stay_page = factory.Faker('text')
    front_page_stay = factory.Faker('text')
    front_page_participate = factory.Faker('text')
    announcement = factory.Faker('text')

    house_access_code = factory.Faker('word')
    ssid = factory.Faker('word')
    ssid_password = factory.Faker('word')

    timezone = factory.Iterator(['America/Los_Angeles', 'Europe/Berlin'])
    bank_account_number = factory.Faker('random_int')
    routing_number = factory.Faker('random_int')

    bank_name = factory.Faker('word')
    name_on_account = factory.Faker('word')
    email_subject_prefix = factory.Faker('word')

    check_out = factory.Iterator(['11am', '10am', '12pm', '1pm'])
    check_in = factory.Iterator(['2pm', '3pm', '4pm'])

    # only use public for now. 'members' doesn't work and 'link' just makes it
    # harder to browse.
    visibility = factory.Iterator(['public'])

    # JKS how to call this?
    @factory.post_generation
    def house_admins(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.house_admins.add(user)
        else:
            self.house_admins.add(1)

    @factory.post_generation
    def readonly_admins(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.readonly_admins.add(user)

    @factory.post_generation
    def add_backing(self, create, extracted, **kwargs):
        # JKS backings are how residents are determined. backings will generate
        # users.
        pass


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
    # JKS add backing


# Note: this doesn't get used because it's really just an indexing mechanism to
# reference what fees should be applied to the bill. Maybe worth wiring up at
# some point but it's a known orphan at the moment.
class LocationFeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationFee

    location = factory.SubFactory(LocationFactory)
    fee = factory.SubFactory(FeeFactory)


class LocationMenuFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationMenu

    location = factory.SubFactory(LocationFactory)
    name = factory.Faker('text', max_nb_chars=15)


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
    start_date = factory.Faker('past_datetime')
    quantity = factory.Iterator([1, 2])
    accept_drft = factory.Faker('pybool')


class BackingFactory(factory.DjangoModelFactory):
    pass
