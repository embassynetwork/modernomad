from django.test import TestCase
from api.commands.bookings import *
from datetime import date, timedelta
from core.factories import *


class CommandErrorMatchers:
    def executeCommandFails(self):
        self.executeCommand()
        self.assertEqual(self.succeeded, False)

    def executeCommandSucceeds(self):
        self.executeCommand()
        if not self.succeeded:
            print "failed with errors " + str(self.result.errors)
            self.assertEqual(self.succeeded, True)

    def executeCommand(self):
        self.succeeded = self.command.execute()
        self.result = self.command.result()

    def assertErrorOn(self, key):
        error = self.result.errors.get(key)
        self.assertNotEqual(error, None)


def on_day(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


class RequestBookingTestCase(TestCase, CommandErrorMatchers):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.location = self.resource.location

    def test_that_depart_is_required(self):
        self.command = RequestBooking(self.user, arrive=on_day(5), resource=self.resource.pk)
        self.executeCommandFails()
        self.assertErrorOn('depart')

    def test_that_resource_is_required(self):
        self.command = RequestBooking(self.user, arrive=on_day(5), depart=on_day(10))
        self.executeCommandFails()
        self.assertErrorOn('resource')

    def test_that_valid_resource_is_required(self):
        self.command = RequestBooking(self.user, arrive=on_day(5), depart=on_day(10), resource="12345")
        self.executeCommandFails()
        self.assertErrorOn('resource')

    def test_that_depart_before_arrive_fails(self):
        self.command = RequestBooking(self.user, arrive=on_day(5), depart=on_day(3), resource=self.resource.pk)
        self.executeCommandFails()
        self.assertErrorOn('depart')

    def test_that_depart_must_be_within_max_booking_days(self):
        self.location.max_booking_days = 20
        self.location.save()

        self.command = RequestBooking(self.user, arrive=on_day(5), depart=on_day(26), resource=self.resource.pk)
        self.executeCommandFails()
        self.assertErrorOn('depart')

    def test_that_command_with_valid_data_creates_booking_and_use(self):
        print str(self.resource)
        print str(self.resource.pk)
        self.command = RequestBooking(self.user, arrive=on_day(5), depart=on_day(10), resource=self.resource.pk)
        self.executeCommandSucceeds()
