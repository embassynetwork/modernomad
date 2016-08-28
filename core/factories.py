import factory
from models import *


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location

    name = "Some Location"
    slug = "someloc"
    latitude = 1.0
    longitude = 2.0


class ResourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Resource

    name = "Chamber of Salons"
    default_rate = 100
    location = factory.SubFactory(LocationFactory)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = "bilbo"
