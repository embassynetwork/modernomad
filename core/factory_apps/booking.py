from . import factory
from core.models import Fee


class FeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Fee

    description = factory.faker('text')
    percentage = factory.faker('pyfloat', left_digits=0, positive=True)
    paid_by_house = factory.faker('pybool')
