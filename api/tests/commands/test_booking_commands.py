from django.test import TestCase
from api.commands.bookings import *
from datetime import date, timedelta
from modernomad.core.factories import *


class CommandErrorMatchers:
    def executeCommandFails(self):
        self.executeCommand()
        self.assertEqual(self.succeeded, False)

    def executeCommandSucceeds(self):
        self.executeCommand()
        if not self.succeeded:
            self.assertEqual(self.succeeded, True)

    def executeCommand(self):
        self.succeeded = self.command.execute()
        self.result = self.command.result()

    def assertErrorOn(self, key):
        error = self.result.errors.get(key)
        self.assertNotEqual(error, None)

    def assertModelSaved(self, model, values={}):
        self.assertTrue(model)
        self.assertTrue(model.pk)
        for key, value in values.items():
            self.assertEqual(getattr(model, key), value)


def on_day(offset, serialized=True):
    result = (date.today() + timedelta(days=offset))
    if serialized:
        return result.isoformat()
    else:
        return result


class RequestBookingTestCase(TestCase, CommandErrorMatchers):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory(default_rate=123.5)
        self.location = self.resource.location
        self.valid_params = {
            'arrive': on_day(5), 'depart': on_day(10), 'resource': self.resource.pk,
            'comments': "this is a great booking"
        }

    def test_that_depart_is_required(self):
        self.command = RequestBooking(self.user, arrive=on_day(5), resource=self.resource.pk)
        self.executeCommandFails()
        self.assertErrorOn('depart')

    # def test_that_user_is_required(self):
    #     self.command = RequestBooking(None, **self.valid_params)
    #     self.executeCommandFails()

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
        self.command = RequestBooking(self.user, **self.valid_params)
        self.executeCommandSucceeds()

        self.assertModelSaved(self.result.data['booking'], {
            'comments': "this is a great booking",
            'rate': 123.5
        })

        self.assertModelSaved(self.result.data['use'], {
            'arrive': on_day(5, False),
            'depart': on_day(10, False),
            'resource': self.resource,
            'location': self.location
        })

    # TODO: bill creation
    # TODO: new_booking_notify
    # TODO: if the user isn't logged in
