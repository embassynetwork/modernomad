from django.test import TestCase
from modernomad.core.factories import *
from api.commands import *
from modernomad.core.models import *
from datetime import date


class CapacityQuantityOnTestCase(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()

    def create_on(self, date, quantity):
        return CapacityChange.objects.create(resource=self.resource, start_date=date, quantity=quantity)

    def test_quantity_is_zero_with_no_capacities(self):
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 13), self.resource), 0)

    def test_quantity_is_zero_before_capacities(self):
        self.create_on(date(4016, 1, 14), 3)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 13), self.resource), 0)

    def test_quantity_after_capacity(self):
        self.create_on(date(4016, 1, 14), 3)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 14), self.resource), 3)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 15), self.resource), 3)

    def test_quantity_doesnt_include_other_resource(self):
        other_resource = ResourceFactory(location=self.resource.location)
        self.create_on(date(4016, 1, 14), 3)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 14), other_resource), 0)

    def test_quantity_with_two_capacities(self):
        self.create_on(date(4016, 1, 14), 3)
        self.create_on(date(4016, 1, 16), 1)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 13), self.resource), 0)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 14), self.resource), 3)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 15), self.resource), 3)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 16), self.resource), 1)
        self.assertEqual(CapacityChange.objects.quantity_on(date(4016, 1, 17), self.resource), 1)
