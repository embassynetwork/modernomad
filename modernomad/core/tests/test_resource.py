from django.test import TestCase
from modernomad.core.factories import *
from api.commands import *
from modernomad.core.models import *
from datetime import date


class ResourceDailyAvailabilitiesBetweenTestCase(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()
        self.start = date(2016, 1, 10)
        self.end = date(2016, 1, 14)
        self.booker = UserFactory()

    def capacity_on(self, date, quantity):
        return CapacityChange.objects.create(resource=self.resource, start_date=date, quantity=quantity)

    def use_on(self, arrive, depart):
        return Use.objects.create(
            resource=self.resource, arrive=arrive,
            depart=depart, status="confirmed",
            user=self.booker)

    def use_on_other_resource(self, arrive, depart):
        resource = ResourceFactory(location=self.resource.location)
        return Use.objects.create(
            resource=resource, arrive=arrive,
            depart=depart, status="confirmed",
            user=self.booker)

    # With no data

    def test_it_returns_zero_quantities_for_each_date_if_resource_has_no_availabilities(self):
        result = self.resource.daily_availabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 0),
            (date(2016, 1, 11), 0),
            (date(2016, 1, 12), 0),
            (date(2016, 1, 13), 0),
            (date(2016, 1, 14), 0)
        ])

    # With capacities only

    def test_it_returns_quantity_for_a_preceeding_capacity(self):
        self.capacity_on(date(2015, 1, 1), 2)

        result = self.resource.daily_availabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 2),
            (date(2016, 1, 11), 2),
            (date(2016, 1, 12), 2),
            (date(2016, 1, 13), 2),
            (date(2016, 1, 14), 2)
        ])

    def test_it_returns_quantity_availabilities_during(self):
        self.capacity_on(date(2016, 1, 12), 3)
        self.capacity_on(date(2016, 1, 14), 2)
        self.capacity_on(date(2016, 1, 15), 6)

        result = self.resource.daily_availabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 0),
            (date(2016, 1, 11), 0),
            (date(2016, 1, 12), 3),
            (date(2016, 1, 13), 3),
            (date(2016, 1, 14), 2)
        ])

    # With uses too

    def test_it_returns_subtracts_confirmed_uses_from_simple_capacity(self):
        self.capacity_on(date(2016, 1, 8), 10)

        self.use_on(date(2016, 1, 8), date(2016, 1, 10))
        self.use_on(date(2016, 1, 9), date(2016, 1, 11))
        self.use_on(date(2016, 1, 12), date(2016, 1, 20))
        self.use_on(date(2016, 1, 13), date(2016, 1, 14))
        self.use_on(date(2016, 1, 15), date(2016, 1, 16))

        result = self.resource.daily_availabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 9),
            (date(2016, 1, 11), 10),
            (date(2016, 1, 12), 9),
            (date(2016, 1, 13), 8),
            (date(2016, 1, 14), 9)
        ])

    def test_it_returns_subtracts_confirmed_bookings(self):
        self.capacity_on(date(2016, 1, 12), 3)
        self.capacity_on(date(2016, 1, 14), 2)
        self.capacity_on(date(2016, 1, 15), 6)

        self.use_on(date(2016, 1, 8), date(2016, 1, 10))
        self.use_on(date(2016, 1, 9), date(2016, 1, 11))
        self.use_on(date(2016, 1, 12), date(2016, 1, 20))
        self.use_on(date(2016, 1, 13), date(2016, 1, 14))
        self.use_on(date(2016, 1, 15), date(2016, 1, 16))

        result = self.resource.daily_availabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), -1),
            (date(2016, 1, 11), 0),
            (date(2016, 1, 12), 2),
            (date(2016, 1, 13), 1),
            (date(2016, 1, 14), 1)
        ])

    def test_it_doesnt_subtract_bookings_for_another_resource(self):
        self.capacity_on(date(2016, 1, 8), 10)

        self.use_on_other_resource(date(2016, 1, 11), date(2016, 1, 14))

        result = self.resource.daily_availabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 10),
            (date(2016, 1, 11), 10),
            (date(2016, 1, 12), 10),
            (date(2016, 1, 13), 10),
            (date(2016, 1, 14), 10)
        ])
