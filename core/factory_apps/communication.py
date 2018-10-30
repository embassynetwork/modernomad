from . import factory
from core import models
from .user import UserFactory


class EmailtemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.EmailTemplate

    body = factory.faker('paragraph')
    subject = factory.faker('words')
    name = factory.faker('words')
    creator = factory.SubFactory(UserFactory)
    shared = factory.faker('pyboolean')
    context = models.EmailTemplate.BOOKING
