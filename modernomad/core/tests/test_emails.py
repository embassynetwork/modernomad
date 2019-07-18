from django.test import TestCase
import unittest
from modernomad.core.factories import ResourceFactory
from django.contrib.auth.models import User
from modernomad.core.models import Payment, Use, Booking, UserProfile, LocationEmailTemplate
from modernomad.core.emails.messages import new_booking_notify, send_booking_receipt, updated_booking_notify, admin_daily_update
from modernomad.core.tasks import send_departure_email, send_guest_welcome, guests_residents_daily_update
from datetime import datetime, timedelta, date
from freezegun import freeze_time

TODAY = date(2019, 3, 14)

@freeze_time(TODAY)
class EmailsTestCase(TestCase):

    def create_booking(self, user, rate=100, status=Use.PENDING, arrive=date(4016, 1, 13), depart=date(4016, 1, 23)):
        u = Use(location=self.resource.location, status=status, user=user, arrive=arrive,
                depart=depart, resource=self.resource, purpose="just because")
        u.save()
        booking = Booking(rate=rate, use=u)
        booking.save() # will generate the bill
        return booking

    def create_user(self, username, email, admin=False, resident=False):
        user = User.objects.create(username=username, first_name='user', last_name='user', email=email)
        user.profile = UserProfile.objects.create(user=user)
        user.save()
        if admin:
            self.resource.location.house_admins.add(user)
        if resident:
            self.resource.set_next_backing([user], datetime.now())
        return user

    def setUp(self):
        # Patch mailgun
        class MockResponse():
            status_code = 200
        self.mock_mailgun_send = unittest.mock.patch('modernomad.core.emails.messages.mailgun_send', return_value=MockResponse())
        self.mock_mailgun_send.start()

        self.resource = ResourceFactory()
        self.guest1 = self.create_user('guest1', email='guest1@bob.com')
        self.guest2 = self.create_user('guest2', email='guest2@bob.com')
        self.guest3 = self.create_user('guest3', email='guest3@bob.com')
        self.resident = self.create_user('resident1', resident=True, email='resident1@bob.com')
        self.admin = self.create_user('admin1', admin=True, email='admin1@bob.com')
        self.booking = self.create_booking(user=self.guest1)

        yesterday = TODAY + timedelta(days=-1)
        in_two_days = TODAY + timedelta(days=2)
        after_that = in_two_days + timedelta(days=1)

        self.departing_today = self.create_booking(arrive=yesterday, depart=TODAY, user=self.guest1, status="confirmed")
        self.arriving_in_two_days = self.create_booking(arrive=in_two_days, depart=after_that, user=self.guest2, status="confirmed")
        self.arriving_today = self.create_booking(arrive=TODAY, depart=after_that, user=self.guest3, status="confirmed")

    def tearDown(self):
        self.mock_mailgun_send.stop()

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
    def test_departure_email(self):
        # test the task, which calls goodbye_email() in emails.py
        self.assertTrue(send_departure_email())


    def test_guest_welcome(self):
        # test the task, which calls guest_welcome() in emails.py
        self.assertTrue(send_guest_welcome())

    def test_guest_welcome_with_location_email_override(self):
        LocationEmailTemplate.objects.create(
            location=self.resource.location,
            key=LocationEmailTemplate.WELCOME,
            text_body="hi {{first_name}}",
            html_body="hi {{first_name}}")
        self.assertTrue(send_guest_welcome())


    def test_guests_residents_daily_update(self):
        # called here directly instead as the task, because we can get the
        # return value and check that all was copacetic
        resp = guests_residents_daily_update(self.resource.location)
        self.assertEqual(resp.status_code, 200)

    def test_admin_daily_update(self):
        # called here directly instead as the task, because we can get the
        # return value and check that all was copacetic
        resp = admin_daily_update(self.resource.location)
        self.assertEqual(resp.status_code, 200)


    # subscriptions
    #def send_subscription_receipt(subscription, bill):
    #def subscription_note_notify(subscription):
    #def admin_new_subscription_notify(subscription):
