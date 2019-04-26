import pytz

from . import factory
from modernomad.core import models

from .user import UserFactory
from .location import LocationFactory
from .location import ResourceFactory
from .location import FeeFactory


class SubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Subscription

    created = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    updated = factory.Faker('past_datetime', tzinfo=pytz.UTC)

    created_by = factory.SubFactory(UserFactory)
    location = factory.SubFactory(LocationFactory)
    user = factory.SubFactory(UserFactory)

    price = factory.Faker('pydecimal', left_digits=3, positive=True)
    description = factory.Faker('words')

    start_date = factory.Faker('future_date', tzinfo=pytz.UTC)
    end_date = factory.Faker('future_date', tzinfo=pytz.UTC)


class BillFactory(factory.DjangoModelFactory):
    '''Bookings, BillLineItem or Subscription'''
    class Meta:
        model = models.Bill

    generated_on = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    comment = factory.Faker('paragraph')


class SubscriptionBillFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SubscriptionBill

    generated_on = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    comment = factory.Faker('paragraph')

    period_start = factory.Faker('future_date', tzinfo=pytz.UTC)
    period_end = factory.Faker('future_date', tzinfo=pytz.UTC)
    subscription = factory.SubFactory(SubscriptionFactory)


class BookingBillFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BookingBill

    generated_on = factory.Faker('past_datetime')
    comment = factory.Faker('paragraph')


class BillLineItem(factory.DjangoModelFactory):
    class Meta:
        model = models.BillLineItem

    bill = factory.SubFactory(BillFactory)
    fee = factory.SubFactory(FeeFactory)

    description = factory.Faker('words')
    amount = factory.Faker('pydecimal', left_digits=3, positive=True)
    paid_by_house = factory.Faker('pybool')
    custom = factory.Faker('pybool')


class UseFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Use

    created = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    updated = factory.Faker('past_datetime', tzinfo=pytz.UTC)

    location = factory.SubFactory(LocationFactory)
    user = factory.SubFactory(UserFactory)
    resource = factory.SubFactory(ResourceFactory)

    status = models.Use.PENDING
    arrive = factory.Faker('future_date', tzinfo=pytz.UTC)
    depart = factory.Faker('future_date', tzinfo=pytz.UTC)
    arrival_time = factory.Faker('words')
    purpose = factory.Faker('paragraph')
    last_msg = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    accounted_by = models.Use.FIAT


class BookingFactory(factory.DjangoModelFactory):
    # deprecated fields not modeled in factory
    class Meta:
        model = models.Booking

    created = factory.Faker('past_datetime', tzinfo=pytz.UTC)
    updated = factory.Faker('past_datetime', tzinfo=pytz.UTC)

    comments = factory.Faker('paragraph')
    rate = factory.Faker('pydecimal', left_digits=3, positive=True)
    uuid = factory.Faker('uuid4')

    bill = factory.SubFactory(BookingBillFactory)
    use = factory.SubFactory(UseFactory)

    @factory.post_generation
    def suppressed_fees(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for fee in extracted:
                self.suppressed_fees.add(fee)


class PaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Payment

    bill = factory.SubFactory(BillFactory)
    user = factory.SubFactory(UserFactory)
    payment_date = factory.Faker('past_datetime', tzinfo=pytz.UTC)

    # payment_service and payment_method may be empty so ignoring those
    paid_amount = factory.Faker('pydecimal', left_digits=3, positive=True)
    transaction_id = factory.Faker('uuid4')
    last4 = factory.Faker('pyint')


class UseNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.UseNote


class SubscriptionNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SubscriptionNote
