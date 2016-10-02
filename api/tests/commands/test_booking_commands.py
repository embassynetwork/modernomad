from django.test import TestCase
from api.commands.bookings import *
from datetime import date, timedelta
from core.factories import *


class RequestBookingTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.valid_arrive = date.today() + timedelta(days=5)
        self.valid_depart = self.valid_arrive + timedelta(days=5)

    def test_that_command_with_missing_fields_fails(self):
        command = RequestBooking(
            self.user,
            arrive=self.valid_arrive.isoformat()
        )

        command.execute()
        print str(command.result().serialize())

        # self.assertFalse(command.execute())
        # print command.result()

    # def test_that_command_with_valid_data_creates_booking_and_use(self):
    #     command = UpdateOrAddCapacityChange(
    #         self.user,
    #         arrive=self.valid_arrive.isoformat(), depart=self.valid_depart.isoformat()
    #     )
    #     self.assertEqual('fish', self.valid_arrive)
