from django.test import TestCase
from core.factories import *
from api.commands import *
from core.models import *

class AddAvailabilityChangeTestCase(TestCase):
    def setUp(self):
        self.user = None
        self.resource = ResourceFactory()

    def test_command_with_valid_data_creates_an_availability(self):
        command = AddAvailabilityChange(self.user, start_date = "4016-01-13", resource = self.resource.pk, quantity = 2)

        if command.is_valid():
            command.execute()
        else:
            print command.errors()
            self.assertTrue(False)

        availability = Availability.objects.filter(resource = self.resource).last()
        self.assertTrue(availability)
        self.assertEqual(availability.quantity, 2)
        self.assertEqual(availability.start_date, datetime.date(4016, 1, 13))
