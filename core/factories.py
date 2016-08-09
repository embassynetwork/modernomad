import factory
from models import *

class LocationFactory(factory.Factory):
    class Meta:
        model = Location

    name = "Some Location"
    slug = "someloc"
    latitude = 1.0
    longitude = 2.0
