from django.test import TestCase
from core.factories import *
from api.commands import *
from core.models import *
from datetime import date


class AvailabilityQuantityOnTestCase(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()

    def create_on(self, date, quantity):
        return Availability.objects.create(resource=self.resource, start_date=date, quantity=quantity)

    def test_quantity_is_zero_with_no_availabilities(self):
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 13)), 0)

    def test_quantity_is_zero_before_availabilities(self):
        self.create_on(date(4016, 1, 14), 3)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 13)), 0)

    def test_quantity_after_availability(self):
        self.create_on(date(4016, 1, 14), 3)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 14)), 3)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 15)), 3)

    def test_quantity_with_two_availabilities(self):
        self.create_on(date(4016, 1, 14), 3)
        self.create_on(date(4016, 1, 16), 1)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 13)), 0)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 14)), 3)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 15)), 3)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 16)), 1)
        self.assertEqual(Availability.objects.quantity_on(date(4016, 1, 17)), 1)
