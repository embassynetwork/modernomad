from . import factory
from core.models import Fee


class FeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Fee

    description = factory.faker('text')
    percentage = factory.faker('pyfloat', left_digits=0, positive=True)
    paid_by_house = factory.faker('pybool')


class BillFactory(factory.DjangoModelFactory):
    pass


class BillLineItem(factory.DjangoModelFactory):
    pass


class SubscriptionFactory(factory.DjangoModelFactory):
    pass


class SubscriptionBillFactory(factory.DjangoModelFactory):
    pass


class BookingBillFactory(factory.DjangoModelFactory):
    pass


class UseFactory(factory.DjangoModelFactory):
    pass


class BookingFactory(factory.DjangoModelFactory):
    pass


class PaymentFactory(factory.DjangoModelFactory):
    pass


class UseNoteFactory(factory.DjangoModelFactory):
    pass


class SubscriptionNoteFactory(factory.DjangoModelFactory):
    pass

