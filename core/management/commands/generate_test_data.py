import contextlib
import io

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

from faker import Faker

from core.factory_apps.communication import EmailtemplateFactory
from core.factory_apps.location import LocationFactory, ResourceFactory
from core.factory_apps.user import SuperUserFactory


class Command(BaseCommand):
    help = 'Generate test data for a development environment.'

    def handle(self, *args, **options):
        # setting the seed so output is consistent
        fake = Faker()
        fake.seed(1)

        # create a known super user. this user will also be set as a location admin for
        # all locations.
        SuperUserFactory()

        # communication. these emails will also generate users.
        EmailtemplateFactory()

        # The email sending tasks expect there to be locations with these slugs
        location = LocationFactory(slug="embassysf", name="Embassy SF")
        ResourceFactory(location=location, name="Batcave")
        ResourceFactory(location=location, name="Ada Lovelace")

        location = LocationFactory(slug="amsterdam", name="Embassy Amsterdam")
        ResourceFactory(location=location, name="Some room")

        location = LocationFactory(slug="redvic", name="The Red Victorian")
        ResourceFactory(location=location, name="Another room")



        self.stdout.write(self.style.SUCCESS('Successfully generated testdata'))
