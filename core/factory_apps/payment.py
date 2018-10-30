from . import factory
from core.models import Fee
from core import models


class FeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Fee

    description = factory.faker('text')
    percentage = factory.faker('pyfloat', left_digits=0, positive=True)
    paid_by_house = factory.faker('pybool')


class BillFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Bill


class BillLineItem(factory.DjangoModelFactory):
    class Meta:
        model = models.BillLineItem


class SubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Subscription


class SubscriptionBillFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SubscriptionBill


class BookingBillFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BookingBill


class UseFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Use


class BookingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Booking


class PaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Payment


class UseNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.UseNote


class SubscriptionNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SubscriptionNote

