import traceback
from datetime import datetime, timedelta, date

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from core.models import Location, Subscription

class SubscriptionTestCase(TestCase):
	
	def setUp(self):
		self.location = Location.objects.create(latitude="0", longitude="0", name="Test Location", slug="test")
		self.user1 = User.objects.create(username='member_one', first_name='Member', last_name='One')
		
		today = timezone.now().date()
		
		# Starts today and no end
		self.sub1 = Subscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = 100.00, 
			start_date = today
		)

		# Starts today and ends in a month
		self.sub2 = Subscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = 200.00, 
			start_date = today,
			end_date = today + timedelta(days=30)
		)

		# Starts in a month
		self.sub3 = Subscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = 300.00, 
			start_date = today + timedelta(days=30)
		)

		# Started a month ago and ends today
		self.sub4 = Subscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = 400.00, 
			start_date = today - timedelta(days=30),
			end_date = today
		)

		# Ended yesterday
		self.sub5 = Subscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = 500.00, 
			start_date = today - timedelta(days=31),
			end_date = today - timedelta(days=1)
		)

		# All last year
		self.sub6 = Subscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = 600.00, 
			start_date = date(year=today.year-1, month=1, day=1),
			end_date =  date(year=today.year-1, month=12, day=31)
		)
	
	def period_boundery_test(self, period_start, period_end):
		# For a given period start, test the period_end is equal to the given period_end
		s = Subscription(location=self.location, user=self.user1, start_date=period_start)
		ps, pe = s.get_period(target_date=period_start)
		self.assertEquals(pe, period_end)
		
	def test_period_ends(self):
		# Test month bounderies
		self.period_boundery_test(date(2015, 1, 1), date(2015, 1, 31))
		self.period_boundery_test(date(2015, 2, 1), date(2015, 2, 28))
		self.period_boundery_test(date(2015, 3, 1), date(2015, 3, 31))
		self.period_boundery_test(date(2015, 4, 1), date(2015, 4, 30))
		self.period_boundery_test(date(2015, 5, 1), date(2015, 5, 31))
		self.period_boundery_test(date(2015, 6, 1), date(2015, 6, 30))
		self.period_boundery_test(date(2015, 7, 1), date(2015, 7, 31))
		self.period_boundery_test(date(2015, 8, 1), date(2015, 8, 31))
		self.period_boundery_test(date(2015, 9, 1), date(2015, 9, 30))
		self.period_boundery_test(date(2015, 10, 1), date(2015, 10, 31))
		self.period_boundery_test(date(2015, 11, 1), date(2015, 11, 30))
		self.period_boundery_test(date(2015, 12, 1), date(2015, 12, 31))

		# Leap year!
		self.period_boundery_test(date(2016, 2, 1), date(2016, 2, 29))

		# Test Day bounderies
		for i in range(2, 31):
			self.period_boundery_test(date(2015, 7, i), date(2015, 8, i-1))
		
		# Test when the next following month has fewer days
		self.period_boundery_test(date(2015, 1, 29), date(2015, 2, 28))
		self.period_boundery_test(date(2015, 1, 30), date(2015, 2, 28))
		self.period_boundery_test(date(2015, 1, 31), date(2015, 2, 28))
	
	def test_is_period_boundary(self):
		s = Subscription(location=self.location, user=self.user1, start_date=date(2016,1,1), end_date=date(2016,5,31))
		
		self.assertFalse(s.is_period_boundary(target_date=date(2016, 2, 15)))
		self.assertTrue(s.is_period_boundary(target_date=date(2016, 2, 29)))
		self.assertFalse(s.is_period_boundary(target_date=date(2016, 3, 15)))
		self.assertTrue(s.is_period_boundary(target_date=date(2016, 3, 31)))
		
		self.assertTrue(s.is_period_boundary())
		s.end_date = date(6,1,1)
		self.assertFalse(s.is_period_boundary())
		
	def test_get_period(self):
		today = timezone.now().date()
		
		ps, pe = self.sub1.get_period(target_date=today)
		# The period start day should be the same day as our start date
		self.assertEqual(ps.day, self.sub1.start_date.day)
		
		# Today is outside the date range for this subscription
		self.assertEquals(None, self.sub3.get_period(target_date=today))
	
	def test_total_periods(self):
		self.assertEquals(0, self.sub1.total_periods())
		self.assertEquals(0, self.sub3.total_periods())
		self.assertEquals(1, self.sub5.total_periods())
		self.assertEquals(12, self.sub6.total_periods())
	
	def test_inactive_subscriptions(self):
		inactive_subscriptions = Subscription.objects.inactive_subscriptions()
		self.assertFalse(self.sub1 in inactive_subscriptions)
		self.assertFalse(self.sub2 in inactive_subscriptions)
		self.assertTrue(self.sub3 in inactive_subscriptions)
		self.assertFalse(self.sub4 in inactive_subscriptions)
		self.assertTrue(self.sub5 in inactive_subscriptions)
		self.assertTrue(self.sub6 in inactive_subscriptions)
	
	def test_active_subscriptions(self):
		active_subscriptions = Subscription.objects.active_subscriptions()
		self.assertTrue(self.sub1 in active_subscriptions)
		self.assertTrue(self.sub2 in active_subscriptions)
		self.assertFalse(self.sub3 in active_subscriptions)
		self.assertTrue(self.sub4 in active_subscriptions)
		self.assertFalse(self.sub5 in active_subscriptions)
		self.assertFalse(self.sub6 in active_subscriptions)
	
	def test_is_active(self):
		self.assertTrue(self.sub1.is_active())
		self.assertTrue(self.sub2.is_active())
		self.assertFalse(self.sub3.is_active())
		self.assertTrue(self.sub4.is_active())
		self.assertFalse(self.sub5.is_active())
	
	def test_generate_bill(self):
		today = timezone.now().date()
		
		# Assume that if we generate a bill we will have a bill
		self.assertEquals(0, self.sub1.bills.count())
		self.sub1.generate_bill(target_date=today)
		self.assertEquals(1, self.sub1.bills.count())

		bill = self.sub1.bills.first()
		self.assertEquals(self.sub1.price, bill.amount())

		ps, pe = self.sub1.get_period(target_date=today)
		self.assertEquals(ps, bill.period_start)
		self.assertEquals(pe, bill.period_end)
	
	def test_generate_all_bills(self):
		self.assertEquals(0, self.sub6.bills.count())
		self.sub6.generate_all_bills()
		self.assertEquals(12, self.sub6.bills.count())
