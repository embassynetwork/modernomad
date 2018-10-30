from . import factory
from core import models
from .user import UserFactory


class EmailtemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.EmailTemplate

    body = factory.Faker('paragraph')
    subject = factory.Faker('words')
    name = factory.Faker('words')
    creator = factory.SubFactory(UserFactory)
    shared = factory.Faker('pyboolean')
    context = models.EmailTemplate.BOOKING
