import traceback
from datetime import datetime, timedelta, date

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from core.models import Location, CommunitySubscription

class SubscriptionTestCase(TestCase):

	def setUp(self):
		self.location = Location.objects.create(latitude="0", longitude="0", name="Test Location", slug="test")
		self.user1 = User.objects.create(username='member_one', first_name='Member', last_name='One')
		
		today = timezone.now().date()
		
		# Starts today and no end
		self.sub1 = CommunitySubscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = "1", 
			start_date = today
		)

		# Starts today and ends in a month
		self.sub2 = CommunitySubscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = "1", 
			start_date = today,
			end_date = today + timedelta(days=30)
		)

		# Starts in a month
		self.sub3 = CommunitySubscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = "1", 
			start_date = today + timedelta(days=30)
		)

		# Started a month ago and ends today
		self.sub4 = CommunitySubscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = "1", 
			start_date = today - timedelta(days=30),
			end_date = today
		)

		# Ended yesterday
		self.sub5 = CommunitySubscription.objects.create(
			location = self.location, 
			user = self.user1, 
			price = "1", 
			start_date = today - timedelta(days=31),
			end_date = today - timedelta(days=1)
		)


	def test_total_periods(self):
		self.assertEquals(0, self.sub1.total_periods())
		self.assertEquals(1, self.sub5.total_periods())

	def test_inactive_subscriptions(self):
		inactive_subscriptions = CommunitySubscription.objects.inactive_subscriptions()
		self.assertFalse(self.sub1 in inactive_subscriptions)
		self.assertFalse(self.sub2 in inactive_subscriptions)
		self.assertTrue(self.sub3 in inactive_subscriptions)
		self.assertFalse(self.sub4 in inactive_subscriptions)
		self.assertTrue(self.sub5 in inactive_subscriptions)


	def test_active_subscriptions(self):
		active_subscriptions = CommunitySubscription.objects.active_subscriptions()
		self.assertTrue(self.sub1 in active_subscriptions)
		self.assertTrue(self.sub2 in active_subscriptions)
		self.assertFalse(self.sub3 in active_subscriptions)
		self.assertTrue(self.sub4 in active_subscriptions)
		self.assertFalse(self.sub5 in active_subscriptions)


	def test_is_active(self):
		self.assertTrue(self.sub1.is_active())
		self.assertTrue(self.sub2.is_active())
		self.assertFalse(self.sub3.is_active())
		self.assertTrue(self.sub4.is_active())
		self.assertFalse(self.sub5.is_active())
	

	def test_generate_bill(self):
		self.sub1.generate_bill()
		self.assertTrue(self.sub1.bills != None)
