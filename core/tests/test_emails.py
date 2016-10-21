from django.test import TestCase
from core.factories import *
from core.models import *
from datetime import date
from core.emails import *

class EmailsTestCase(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()
        self.user = UserFactory()
        u = Use(location=self.resource.location, status=Use.CONFIRMED, user=self.user , arrive=date(4016, 1, 13), 
                depart=date(4016, 1, 23), resource=self.resource, purpose="just because")
        u.save()
        self.booking = Booking(rate=100, use=u)
        self.booking.save() # will generate the bill

    # emails triggered by actions
    def test_new_booking_notify(self):
        resp = new_booking_notify(self.booking)
        self.assertEqual(resp.status_code, 200)

    def test_send_booking_receipt(self):
        pmt = Payment.objects.create(
            payment_method="cash",
            paid_amount=self.booking.bill.total_owed(),
            bill=self.booking.bill,
            user=None,
            transaction_id="Manual"
        )
        pmt.save()
        resp = send_booking_receipt(self.booking)
        self.assertEqual(resp.status_code, 200)


    def test_updated_booking_notify(self):
        resp = updated_booking_notify(self.booking)
        self.assertEqual(resp.status_code, 200)


    # automated emails (called from tasks.py)
    def test_goodbye_email(self):
        # XXX we dont HAVE to test for anything, just run this...
        send_departure_email():

        self.assert_equal(resp.status_code, 200)
        pass

    def test_guest_welcome(self):
        pass

    def test_guests_residents_daily_update(self):
        pass

    def test_admin_daily_update(self):
        pass

    # subscriptions
    #def send_subscription_receipt(subscription, bill):
    #def subscription_note_notify(subscription):
    #def admin_new_subscription_notify(subscription):


