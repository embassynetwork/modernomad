from django.test import TestCase
from core.factories import *
from api.commands import *
from core.models import *
from datetime import date


class ResourceDailyBookabilitiesBetweenTestCase(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()
        self.start = date(2016, 1, 10)
        self.end = date(2016, 1, 14)
        self.booker = UserFactory()

    def availability_on(self, date, quantity):
        return Availability.objects.create(resource=self.resource, start_date=date, quantity=quantity)

    def booking_on(self, arrive, depart):
        return Booking.objects.create(
            resource=self.resource, arrive=arrive,
            depart=depart, status="confirmed",
            user=self.booker)

    def booking_on_other_resource(self, arrive, depart):
        resource = ResourceFactory(location=self.resource.location)
        return Booking.objects.create(
            resource=resource, arrive=arrive,
            depart=depart, status="confirmed",
            user=self.booker)


    # With no data

    def test_it_returns_zero_quantities_for_each_date_if_resource_has_no_availabilities(self):
        result = self.resource.daily_bookabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 0),
            (date(2016, 1, 11), 0),
            (date(2016, 1, 12), 0),
            (date(2016, 1, 13), 0),
            (date(2016, 1, 14), 0)
        ])

    # With availabilities only

    def test_it_returns_quantity_for_a_preceeding_availability(self):
        self.availability_on(date(2015, 1, 1), 2)

        result = self.resource.daily_bookabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 2),
            (date(2016, 1, 11), 2),
            (date(2016, 1, 12), 2),
            (date(2016, 1, 13), 2),
            (date(2016, 1, 14), 2)
        ])

    def test_it_returns_quantity_availabilities_during(self):
        self.availability_on(date(2016, 1, 12), 3)
        self.availability_on(date(2016, 1, 14), 2)
        self.availability_on(date(2016, 1, 15), 6)

        result = self.resource.daily_bookabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 0),
            (date(2016, 1, 11), 0),
            (date(2016, 1, 12), 3),
            (date(2016, 1, 13), 3),
            (date(2016, 1, 14), 2)
        ])

    # With bookings too

    def test_it_returns_subtracts_confirmed_bookings_from_simple_availability(self):
        self.availability_on(date(2016, 1, 8), 10)

        self.booking_on(date(2016, 1, 8), date(2016, 1, 10))
        self.booking_on(date(2016, 1, 9), date(2016, 1, 11))
        self.booking_on(date(2016, 1, 12), date(2016, 1, 20))
        self.booking_on(date(2016, 1, 13), date(2016, 1, 14))
        self.booking_on(date(2016, 1, 15), date(2016, 1, 16))

        result = self.resource.daily_bookabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 9),
            (date(2016, 1, 11), 10),
            (date(2016, 1, 12), 9),
            (date(2016, 1, 13), 8),
            (date(2016, 1, 14), 9)
        ])

    def test_it_returns_subtracts_confirmed_bookings(self):
        self.availability_on(date(2016, 1, 12), 3)
        self.availability_on(date(2016, 1, 14), 2)
        self.availability_on(date(2016, 1, 15), 6)

        self.booking_on(date(2016, 1, 8), date(2016, 1, 10))
        self.booking_on(date(2016, 1, 9), date(2016, 1, 11))
        self.booking_on(date(2016, 1, 12), date(2016, 1, 20))
        self.booking_on(date(2016, 1, 13), date(2016, 1, 14))
        self.booking_on(date(2016, 1, 15), date(2016, 1, 16))

        result = self.resource.daily_bookabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), -1),
            (date(2016, 1, 11), 0),
            (date(2016, 1, 12), 2),
            (date(2016, 1, 13), 1),
            (date(2016, 1, 14), 1)
        ])

    def test_it_doesnt_subtract_bookings_for_another_resource(self):
        self.availability_on(date(2016, 1, 8), 10)

        self.booking_on_other_resource(date(2016, 1, 11), date(2016, 1, 14))

        result = self.resource.daily_bookabilities_within(self.start, self.end)
        self.assertEqual(result, [
            (date(2016, 1, 10), 10),
            (date(2016, 1, 11), 10),
            (date(2016, 1, 12), 10),
            (date(2016, 1, 13), 10),
            (date(2016, 1, 14), 10)
        ])
