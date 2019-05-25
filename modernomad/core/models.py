# -*- coding: utf-8 -*-
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.db import models
from PIL import Image
import os
import datetime
from django.conf import settings
from django.core.files.storage import default_storage
import uuid
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.flatpages.models import FlatPage
from modernomad.core.libs.dates import dates_within, count_range_objects_on_day
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
import pytz

# imports for signals
import django.dispatch
from django.dispatch import receiver
from django.db.models.signals import pre_save, m2m_changed

# bank app imports
from bank.models import Account, Transaction, Currency

import logging
logger = logging.getLogger(__name__)

# there is a weird db issue it seems with setting a field to null=False after it has been defined as null=True.
# see http://od-eon.com/blogs/stefan/adding-not-null-column-south/ and
# http://south.aeracode.org/ticket/782
# one suggestion was to try setting default value in the model file, but this hasn't worked either.
# currently the field are still set to null=True, though they shouldn't be.


def location_img_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # rename file to random string
    filename = "%s.%s" % (uuid.uuid4(), ext.lower())

    upload_path = "locations/"
    upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    if not os.path.exists(upload_abs_path):
        os.makedirs(upload_abs_path)
    return os.path.join(upload_path, filename)


def default_location():
    return Location.objects.get(pk=1)


LOCATION_PUBLIC = 'public'
LOCATION_MEMBER = 'members'
LOCATION_LINK = 'link'

class Location(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(
            max_length=60, unique=True,
            help_text="Try to make this short and sweet. It will also be used to form several location-specific " +
            "email addresses in the form of xxx@<your_slug>.mail.embassynetwork.com"
            )
    short_description = models.TextField()
    address = models.CharField(max_length=300)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to=location_img_upload_to, help_text="Requires an image with proportions 800px wide x 225px high")
    profile_image = models.ImageField(
            upload_to=location_img_upload_to,
            help_text="A shiny high profile image for the location. Must be 336x344px.", null=True, blank=True
            )
    stay_page = models.TextField(
            default="This is the page which has some descriptive text at the top (this text), and then lists the " +
            "available rooms. HTML is supported."
            )
    front_page_stay = models.TextField(
            default="This is the middle of three sections underneath the main landing page text to entice people to " +
            "stay with you, and then links to the stay page (above). HTML is supported."
            )
    front_page_participate = models.TextField(
            default="This is far right of three sections underneath the main landing page text to tell people how to get " +
            "involved with your community. There is a link to the Events page underneath. HTML is supported. "
            )
    announcement = models.TextField(
            blank=True, null=True,
            default="This is far left of three sections underneath the main landing page text to use for announcements and news. HTML is supported."
            )
    max_booking_days = models.IntegerField(default=14)
    welcome_email_days_ahead = models.IntegerField(default=2)
    house_access_code = models.CharField(max_length=50, blank=True, null=True)
    ssid = models.CharField(max_length=200, blank=True, null=True)
    ssid_password = models.CharField(max_length=200, blank=True, null=True)
    timezone = models.CharField(
            max_length=200,
            help_text="Must be an accurate timezone name, eg. \"America/Los_Angeles\". Check here for your time zone: " +
            "http://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            )
    bank_account_number = models.IntegerField(blank=True, null=True, help_text="We use this to transfer money to you!")
    routing_number = models.IntegerField(blank=True, null=True, help_text="We use this to transfer money to you!")
    bank_name = models.CharField(max_length=200, blank=True, null=True, help_text="We use this to transfer money to you!")
    name_on_account = models.CharField(max_length=200, blank=True, null=True, help_text="We use this to transfer money to you!")
    email_subject_prefix = models.CharField(max_length=200, help_text="Your prefix will be wrapped in square brackets automatically.")
    house_admins = models.ManyToManyField(User, related_name='house_admin')
    readonly_admins = models.ManyToManyField(
            User, related_name='readonly_admin', blank=True,
            help_text="Readonly admins do not show up as part of the community. Useful for eg. external bookkeepers, etc."
            )
    check_out = models.CharField(max_length=20, help_text="When your guests should be out of their bed/room.")
    check_in = models.CharField(max_length=200, help_text="When your guests can expect their bed to be ready.")

    visibility_options = (
        (LOCATION_PUBLIC, 'Public'),
        (LOCATION_MEMBER, 'Members Only'),
        (LOCATION_LINK, 'Those with the Link')
    )
    visibility = models.CharField(max_length=32, choices=visibility_options, blank=False, null=False, default='link')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('location_detail', kwargs={'location_slug': self.slug})

    def from_email(self):
        ''' return a location-specific email in the standard format we use.'''
        return "stay@%s.mail.embassynetwork.com" % self.slug

    def get_rooms(self):
        return list(Resource.objects.filter(location=self))

    def get_members(self):
        active_subscriptions = Subscription.objects.active_subscriptions().filter(location=self)
        subscribers = []
        for s in active_subscriptions:
            subscribers.append(s.user)
        return list(list(self.residents()) + list(self.house_admins.all()) + list(self.event_admin_group.users.all()) + subscribers)

    def rooms_with_future_capacity_choices(self):
        choices = []
        rooms = self.rooms_with_future_capacity()
        for room in rooms:
            choices.append((room.id, room.name))
        return choices

    def rooms_with_future_capacity(self):
        future_capacity = []
        for room in Resource.objects.filter(location=self).prefetch_related('capacity_changes'):
            if room.has_future_capacity():
                future_capacity.append(room)
        return future_capacity

    def rooms_with_future_drft_capacity(self):
        future_capacity = []
        for room in Resource.objects.filter(location=self).prefetch_related('capacity_changes'):
            if (room.has_future_capacity() and room.has_future_drft_capacity()):
                future_capacity.append(room)
        return future_capacity

    def reservable_rooms_on_day(self, the_day):
        rooms_at_location = self.filter(location=self)
        return [room for room in rooms_at_location if room.capacity_on(the_day)]

    def capacity(self, start, end):
        # show capacity (occupied and free beds), between start and end
        # dates, per location. create a structure queryable by
        # available_beds[room][date] = n, where n is the number of beds free.
        rooms_at_location = self.get_rooms()
        available_beds = {}
        for room in rooms_at_location:
            the_day = start
            available_beds[room] = []
            while the_day < end:
                uses_today = Use.objects.confirmed_approved_on_date(the_day, self, resource=room)
                free_beds = room.capacity_on(the_day) - len(uses_today)
                available_beds[room].append({'the_date': the_day, 'beds_free': free_beds})
                the_day = the_day + datetime.timedelta(1)
        return available_beds

    def rooms_free(self, arrive, depart):
        available = list(self.resources.all())
        for room in self.get_rooms():
            the_day = arrive
            while the_day < depart:
                # if there is any day the room isn't available, then the room
                # isn't free the whole time
                if not room.available_on(the_day):
                    available.remove(room)
                    break
                the_day = the_day + datetime.timedelta(1)
        return available

    def has_capacity(self, arrive=None, depart=None):
        if not arrive:
            arrive = timezone.localtime(timezone.now())
            depart = arrive + datetime.timedelta(1)
        if self.rooms_free(arrive, depart):
            return True
        return False

    def events(self, user=None):
        if 'gather' in settings.INSTALLED_APPS:
            from gather.models import Event
            return Event.objects.upcoming(upto=5, current_user=user, location=self)
        return None

    def coming_month_events(self, days=30):
        today = timezone.localtime(timezone.now())
        if 'gather' in settings.INSTALLED_APPS:
            from gather.models import Event
            return Event.objects.filter(status="live").filter(location=self).exclude(end__lt=today) \
                        .exclude(start__gte=today+datetime.timedelta(days=days))
        return None

    def coming_month_uses(self, days=30):
        today = timezone.localtime(timezone.now())
        return (Use.objects
            .filter(Q(status="confirmed") | Q(status="approved"))
            .filter(location=self)
            .exclude(depart__lt=today)
            .exclude(arrive__gt=today+datetime.timedelta(days=days))
            .select_related('user__profile')
        )

    def people_today(self):
        guests = self.guests_today()
        residents = list(self.residents())
        active_subscriptions = Subscription.objects.active_subscriptions().filter(location=self)
        members = []
        for s in active_subscriptions:
            members.append(s.user)
        return (guests+residents+members)

    def people_in_coming_month(self):
        # pull out all bookings in the coming month
        people = []
        for use in self.coming_month_uses():
            if use.user not in people:
                people.append(use.user)

        # add residents to the list of people in the house in the coming month.
        for r in self.residents():
            if r not in people:
                people.append(r)

        # add house admins
        for a in self.house_admins.all().select_related('profile'):
            if a not in people:
                people.append(a)

        # Add all the people from events too
        for e in self.coming_month_events():
            for u in e.organizers.all():
                if u not in people:
                    people.append(u)

        return people

    def guests_today(self):
        today = timezone.now()
        uses_today = Use.objects.filter(location=self) \
                        .filter(Q(status="confirmed") | Q(status="approved")) \
                        .exclude(depart__lt=today).exclude(arrive__gt=today)
        guests_today = []
        for r in uses_today:
            if r.user not in guests_today:
                guests_today.append(r.user)
        return guests_today

    def get_menus(self):
        return LocationMenu.objects.filter(location=self)

    def tz(self):
        if self.timezone:
            return pytz.timezone(self.timezone)
        else:
            return None

    def residents(self):
        all_residents = []
        for resource in self.resources.all():
            for resident in resource.backers():
                all_residents.append(resident)
        return all_residents


class LocationNotUniqueException(Exception):
    pass


class LocationDoesNotExistException(Exception):
    pass


def get_location(location_slug):
    if location_slug:
        try:
            location = Location.objects.filter(slug=location_slug).first()
        except:
            raise LocationDoesNotExistException("The requested location does not exist: %s" % location_slug)
    else:
        if Location.objects.count() == 1:
            location = Location.objects.get(id=1)
        else:
            raise LocationNotUniqueException(
                "You did not specify a location and yet there is more than one location defined. Please specify a location."
            )
    return location


def resource_img_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # rename file to random string
    filename = "%s.%s" % (uuid.uuid4(), ext.lower())

    upload_path = "rooms/"
    upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    if not os.path.exists(upload_abs_path):
        os.makedirs(upload_abs_path)
    return os.path.join(upload_path, filename)


class ResourceManager(models.Manager):
    def backed_by(self, user):
        resources = self.get_queryset().filter(backing__money_account__owners=user)
        return resources


class Resource(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, related_name='resources', null=True)
    default_rate = models.DecimalField(decimal_places=2, max_digits=9)
    description = models.TextField(blank=True, null=True, help_text="Displayed on room detail page only")
    summary = models.CharField(max_length=140, help_text="Displayed on the search page. Max length 140 chars", default='')
    cancellation_policy = models.CharField(max_length=400, default="24 hours")
    image = ProcessedImageField(
        help_text="Should be 500x325px or a 1 to 0.65 ratio. If it is not this size, it will automatically be resized.",
        upload_to=resource_img_upload_to,
        processors=[ResizeToFill(500, 325)],
        format='JPEG',
        options={'quality': 90})
    objects = ResourceManager()

    def __str__(self):
        return self.name

    def quantity_between(self, start, end):
        total = 0
        the_day = start
        while the_day < end:
            total += self.capacity_on(the_day)
            the_day += datetime.timedelta(1)
        return total

    def confirmed_uses_between(self, start, end):
        return self.use_set.confirmed_between_dates(start, end)

    def has_future_drft_capacity(self):
        return self.has_future_capacity(accept_drft=True)

    def has_future_capacity(self, accept_drft=False):
        today = timezone.localtime(timezone.now()).date()
        # iterate backwards over time through capacities. if there's any
        # non-zero capacities current or future, then this resource has
        # SOME 'future' capacity.
        avails = self.capacity_changes.all()
        if accept_drft:
            avails = avails.filter(accept_drft=True)
        # do sort outside database so prefetch_related works
        avails = sorted(list(avails), key=lambda obj: obj.start_date, reverse=True)
        for a in avails:
            if a.start_date >= today and a.quantity > 0:
                return True
            # we only ever want to go one capacity into the past.
            elif a.start_date < today:
                if a.quantity > 0:
                    return True
                else:
                    return False

    def capacity_on(self, this_day):
        # returns quantity (an integer).
        return CapacityChange.objects.quantity_on(this_day, self)

    def drftable_on(self, this_day):
        # returns True or False
        return CapacityChange.objects.drft_on(this_day, self)

    def available_on(self, this_day):
        # a resource is available if it has capacity that is not already
        # used. returns True or False.
        capacities = self.capacity_on(this_day)
        if not capacities:
            return False
        uses_on_this_day = Use.objects.confirmed_approved_on_date(this_day, self.location, resource=self)
        if len(uses_on_this_day) < capacities:
            return True
        else:
            return False

    def drftable_between(self, start, end):
        # note this just checks if the resource has drftable capacity, not
        # whether it has _availability_. (ie, it migt be drftable but booked).
        for day in dates_within(start, end):
            if not self.drftable_on(day):
                return False
        return True

    def available_between(self, start, end):
        # note this just checks if the resource has drftable capacity, not
        # whether it has _availability_. (ie, it migt be drftable but booked).
        for day in dates_within(start, end):
            if not self.available_on(day):
                return False
        return True

    def daily_capacities_within(self, start, end):
        '''
        Param:
            start datetime
            end datetime
        Returns a list [(day, quantity), ...]
        '''
        def capacities_between(start, end):
            '''
            Returns all the capacity change objects that affect the time period
            described, in chronological order. This includes the immediately before or on
            the start date, and any others through to and including the end date.
            '''
            capacities = self.capacity_changes.exclude(start_date__gt=end).order_by('-start_date')
            capacities_between = []
            for a in capacities:
                # since we already filtered out capacities ahead of our date
                # range, we just need to go backwards until the first avail that
                # starts on or before our start date, and then break.
                if a.start_date > start:
                    capacities_between.append(a)
                else:
                    capacities_between.append(a)
                    break
            capacities_between.reverse()
            return capacities_between

        capacities = capacities_between(start, end)
        quantity = 0
        result = []
        for day in dates_within(start, end):
            if capacities and capacities[0].start_date <= day:
                quantity = capacities.pop(0).quantity
            result.append((day, quantity))

        return result

    def daily_availabilities_within(self, start, end):
        '''
        Param:
            start: datetime
            end: datetime

        Returns a list [(day, quantity), ...]
        Quantity = capacity - confirmed usage
        '''
        daily_capacities = self.daily_capacities_within(start, end)
        uses = self.confirmed_uses_between(start, end)

        result = []
        for daily_capacity in daily_capacities:
            day = daily_capacity[0]
            use_quantity = count_range_objects_on_day(uses, day)
            result_quantity = daily_capacity[1] - use_quantity
            result.append((day, result_quantity))

        return result

    def max_daily_capacities_between(self, start, end):
        max_quantity = 0
        avails = self.capacity_changes.exclude(start_date__gt=end).order_by('-start_date')
        for a in avails:
            if a.quantity > max_quantity:
                max_quantity = a.quantity
            if a.start_date <= start:
                break
        return max_quantity

    def tz(self):
        assert self.location, "You can't fetch a timezone on a resource without a location"
        return self.location.tz()

    def backers(self):
        b = self.current_backing()
        if b:
            return b.users.all().select_related('profile')
        else:
            return []

    def backings_this_room(self):
        return self.backings.all()

    def current_backing(self):
        today = timezone.localtime(timezone.now()).date()
        soonest_backing = self.current_and_future_backings().first()
        if (not soonest_backing) or (soonest_backing and soonest_backing.start > today):
            return None
        else:
            return soonest_backing

    def current_backers(self):
        if self.current_backing():
            return self.current_backing().users.all()
        else:
            return []

    def current_backers_for_display(self):
        return ["%s %s" % (u.first_name, u.last_name) for u in self.current_backers()]

    def scheduled_future_backings(self):
        today = timezone.localtime(timezone.now()).date()
        future = self.backings_this_room().filter(start__gt=today)
        return future

    def latest_backing(self):
        # latest backing *may* be in the past or the future...
        return self.backings_this_room().order_by('start').last()

    def current_and_future_backings(self, date=None):
        if not date:
            date = timezone.localtime(timezone.now()).date()
        # most recent *could* be in the past OR future.
        most_recent = self.backings_this_room().filter(start__lte=date).order_by('start').last()

        # if there was no most_recent, or if most_recent backing ended in
        # the past, then only look for future backings.
        if (not most_recent) or (hasattr(most_recent, 'end') and most_recent.end and most_recent.end <= date):
            # checking if most_recent.end is less than OR equal to 'date' means
            # that if the backing ended today then it is NOT current (much like
            # a departure date of a booking).
            return self.backings_this_room().filter(start__gt=date)
        else:
            # (will include most_recent)
            return self.backings_this_room().filter(start__gte=most_recent.start)

    def set_next_backing(self, backers, new_backing_date):
        # this method only supports having a single backing in the future.
        # remove all future backings, if any, and then setup the new backing.
        today = timezone.localtime(timezone.now()).date()
        logger.debug('in set_next_backing')
        if hasattr(self, 'backings'):
            logger.debug('will end/delete current and future backings')
            logger.debug(self.current_and_future_backings(new_backing_date))
            for b in self.current_and_future_backings(new_backing_date):
                # if the backing started in the past, then there are likely
                # credits that will need to be reflected to this backer. so
                # don't delete the backing, just end it. but if the backing
                # hasn't even started yet, then just kill it and replace it
                # with the new one.
                if (b.start > today) or (b.start == new_backing_date):
                    logger.debug('deleting backing %d' % b.id)
                    b.delete()
                else:
                    logger.debug('ending backing %d' % b.id)
                    b.end = new_backing_date
                    b.save()
        # create a new backing
        new_backing = Backing.objects.setup_new(resource=self, backers=backers, start=new_backing_date)
        logger.debug('created new backing %d' % new_backing.id)


class Fee(models.Model):
    description = models.CharField(max_length=100, verbose_name="Fee Name")
    percentage = models.FloatField(default=0, help_text="For example 5.2% = 0.052")
    paid_by_house = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class UseManager(models.Manager):

    def on_date(self, the_day, status, location):
        # return the bookings that intersect this day, of any status
        all_on_date = super(UseManager, self).get_queryset().filter(location=location).filter(arrive__lte=the_day).filter(depart__gt=the_day)
        return all_on_date.filter(status=status)

    def confirmed_between_dates(self, start, end):
        return self.filter(depart__gte=start, arrive__lte=end).filter(status__in=["approved", "confirmed"])

    def confirmed_approved_on_date(self, the_day, location, resource=None):
        # return the approved or confirmed bookings that intersect this day
        approved_bookings = self.on_date(the_day, status="approved", location=location)
        confirmed_bookings = self.on_date(the_day, status="confirmed", location=location)
        if resource:
            approved_bookings = approved_bookings.filter(resource=resource)
            confirmed_bookings = confirmed_bookings.filter(resource=resource)
        return (list(approved_bookings) + list(confirmed_bookings))

    def confirmed_on_date(self, the_day, location, resource=None):
        confirmed_bookings = self.on_date(the_day, status="confirmed", location=location)
        if resource:
            confirmed_bookings = confirmed_bookings.filter(resource=resource)
        return list(confirmed_bookings)

    def confirmed_but_unpaid(self, location):
        confirmed_this_location = (
            super(UseManager, self).get_queryset()
            .filter(location=location, status='confirmed')
            .order_by('-arrive')
            .select_related('booking', 'booking__bill', 'resource', 'user')
            # this makes is is_paid() efficient
            .prefetch_related('booking__bill__line_items', 'booking__bill__line_items__fee',
                              'booking__bill__payments')
        )
        unpaid_this_location = []
        for use in confirmed_this_location:
            try:
                # use try-except in case the use doesn't have a booking
                # XXX FIXME. this is a horrible hack.
                if not use.booking.bill.is_paid():
                    unpaid_this_location.append(use.booking)
            except:
                pass
        return unpaid_this_location


class Bill(models.Model):
    ''' there are foreign keys (many to one) pointing towards this Bill object
    from Booking, BillLineItem and Payment. Each bill can have many
    bookings, bill line items and many payments. Line items can be accessed
    with the related name bill.line_items, and payments can be accessed with
    the related name bill.payments.'''
    generated_on = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Bill %d" % self.id

    def non_refund_payments(self):
        return self.payments.filter(paid_amount__gt=0)

    def total_paid(self):
        payments = self.payments.all()
        if not payments:
            return 0
        paid = Decimal(0)
        for payment in payments:
            paid = paid + payment.paid_amount
        return paid

    def total_owed(self):
        return self.amount() - self.total_paid()

    def amount(self):
        # Bill amount comes from generated bill line items
        amount = 0
        for line_item in self.line_items.all():
            if not line_item.fee or not line_item.paid_by_house:
                amount = amount + line_item.amount
        return amount

    def total_owed_in_cents(self):
        # this is used to pass the information to stripe, which expects an
        # integer.
        return int(self.total_owed() * 100)

    def subtotal_amount(self):
        # incorporates any manual discounts or fees into the base amount.
        # automatic fees are calculated on top of the total value here.
        base_fees = self.subtotal_items()
        return sum([item.amount for item in base_fees])

    def subtotal_items(self):
        # items that go into the subtotal before calculating taxes and fees.
        # NOTE: will return an *ordered* list with the base resource fee first.

        # the base resource fee is not derived from a standing fee, and is not a custom fee
        base_resource_fee = self.line_items.filter(fee__isnull=True).filter(custom=False)
        # all other line items that go into the subtotal are custom fees
        addl_fees = self.line_items.filter(fee__isnull=True).filter(custom=True)
        return list(base_resource_fee) + list(addl_fees)

    def fees(self):
        # the taxes and fees on top of subtotal
        bill_fees = self.line_items.filter(fee__isnull=False)
        return list(bill_fees)

    def house_fees(self):
        # Pull the house fees from the generated bill line items
        amount = 0
        for line_item in self.line_items.all():
            if line_item.fee and line_item.paid_by_house:
                amount = amount + line_item.amount
        return amount

    def non_house_fees(self):
        # Sum up the user paid (non-house) fees from the bill line items
        amount = 0
        for line_item in self.line_items.all():
            if line_item.fee and not line_item.paid_by_house:
                amount = amount + line_item.amount
        return amount

    def to_house(self):
        return self.amount() - self.non_house_fees() - self.house_fees()

    def is_paid(self):
        return self.total_owed() <= 0

    def time_ordered_payments(self):
        return self.payments.order_by('payment_date')

    def payment_date(self):
        # Date of the last payment
        last_payment = self.payments.order_by('payment_date').reverse().first()
        if last_payment:
            return last_payment.payment_date
        else:
            return None

    def ordered_line_items(self):
        # return bill line items orderer first with the resource item, then the
        # custom items, then the fees
        resource_item = self.line_items.filter(custom=False).filter(fee=None)
        custom_items = self.line_items.filter(custom=True)
        fees = self.line_items.filter(fee__isnull=False)
        return list(resource_item) + list(custom_items) + list(fees)

    def is_booking_bill(self):
        return hasattr(self, 'bookingbill')

    def is_subscription_bill(self):
        return hasattr(self, 'subscriptionbill')


class SubscriptionManager(models.Manager):

    def inactive_subscriptions(self, target_date=None):
        ''' inactive subscriptions all have an end date and those end dates are in the past.'''
        if not target_date:
            target_date = timezone.now().date()
        end_date_exists = Q(end_date__isnull=False)
        end_date_in_past = Q(end_date__lt=target_date)
        future_start = Q(start_date__gt=target_date)
        return self.filter(future_start | (end_date_exists & end_date_in_past)).distinct()

    def active_subscriptions_between(self, start, end):
        ''' returns subscriptions that were active at any points between start
        and end dates.'''
        current = Q(start_date__lte=end)
        unending = Q(end_date__isnull=True)
        future_ending = Q(end_date__gte=start)
        return self.filter(current & (unending | future_ending)).distinct()

    def active_subscriptions(self, target_date=None):
        if not target_date:
            target_date = timezone.now().date()
        current = Q(start_date__lte=target_date)
        unending = Q(end_date__isnull=True)
        future_ending = Q(end_date__gte=target_date)
        return self.filter(current & (unending | future_ending)).distinct()

    def to_be_billed(self, date_window=90):
        subscriptions = []
        starting_point = timezone.now() - timedelta(days=date_window)
        for s in self.filter(updated__gte=starting_point):
            if s.total_periods() < self.bills.count():
                subscriptions.append(s)
        return subscriptions

    def ready_for_billing(self, location, target_date=None):
        if not target_date:
            target_date = timezone.localtime(timezone.now()).date()
        pret_a_manger = []
        active = Subscription.objects.active_subscriptions().filter(location=location)
        for s in active:
            (this_period_start, this_period_end) = s.get_period()
            if this_period_start == target_date:
                pret_a_manger.append(s)
        return pret_a_manger


class Subscription(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="+")
    location = models.ForeignKey(Location)
    user = models.ForeignKey(User)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    description = models.CharField(max_length=256, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    objects = SubscriptionManager()

    def get_period(self, target_date=None):
        ''' get period associated with a certain date. returns None if the
        subscription is not active.'''
        if not target_date:
            target_date = timezone.now().date()

        if target_date < self.start_date or (self.end_date and target_date > self.end_date):
            return (None, None)

        if target_date.day == self.start_date.day:
            period_start = target_date
        else:
            month = target_date.month
            year = target_date.year
            if target_date.day < self.start_date.day:
                if target_date.day == 1:
                    month = 12
                    year = target_date.year - 1
                else:
                    month = target_date.month - 1
            # the period starts on the start_date.day of whatever month we're
            # operating in.
            period_start = date(year, month, self.start_date.day)

        logger.debug('')
        logger.debug('in get_period(). period_start=%s' % period_start)
        logger.debug('')
        period_end = period_start + relativedelta(months=1)
        if period_end.day == period_start.day:
            period_end = period_end - timedelta(days=1)

        return (period_start, period_end)

    def get_next_period_start(self, target_date=None):
        if not target_date:
            target_date = timezone.now().date()
            # if the subscrition starts in the future then the next
            # period is when the subscription starts.
        if self.start_date > target_date:
            return self.start_date
        this_period_start, this_period_end = self.get_period(target_date=target_date)

        if this_period_end is None:
            return None

        next_period_start = this_period_end + timedelta(days=1)
        if self.end_date and next_period_start > self.end_date:
            return None

        return next_period_start

    def is_period_boundary(self, target_date=None):
        if not target_date:
            if not self.end_date:
                return False
            # we need to subtract one day from the end date since otherwise it
            # will be treated as the start of the *next* period. ugh dates.
            target_date = self.end_date - timedelta(days=1)

        period = self.get_period(target_date=target_date)
        return period and period[1] == target_date

    def total_periods(self, target_date=None):
        ''' returns total periods between subscription start date and target
        date.'''
        if not target_date:
            target_date = timezone.now().date()

        if self.start_date > target_date:
            return 0
        if self.end_date and self.end_date < target_date:
            target_date = self.end_date

        rd = relativedelta(target_date + timedelta(days=1), self.start_date)
        return rd.months + (12 * rd.years)

    def bills_between(self, start, end):
        d = start
        bills = []
        while d < end:
            b = self.get_bill_for_date(d)
            if b:
                bills.append(b)
            d = self.get_next_period_start(d)
            if not d:
                break
        return bills

    def get_bill_for_date(self, date):
        result = SubscriptionBill.objects.filter(subscription=self, period_start__lte=date, period_end__gte=date)
        logger.debug('subscription %d: get_bill_for_date %s' % (self.id, date))
        logger.debug('bill object(s):')
        logger.debug(result)
        if result.count():
            if result.count() > 1:
                logger.debug("Warning! Multiple bills found for one date. This shouldn't happen")
                raise Exception('Error: multiple bills for one date:')
            return result[0]
        else:
            return None

    def days_between(self, start, end):
        ''' return the number of days of this subscription that occur between start and end dates'''
        days = 0
        if not self.end_date:
            # set the end date to be the end date passed in so we can work with
            # a date object, but do NOT save.
            self.end_date = end
        if self.start_date >= start and self.end_date <= end:
            days = (self.end_date - self.start_date).days
        elif self.start_date <= start and self.end_date >= end:
            days = (end - start).days
        elif self.start_date < start:
            days = (self.end_date - start).days
        elif self.end_date > end:
            days = (end - self.start_date).days
        return days

    def is_active(self, target_date=None):
        if not target_date:
            target_date = timezone.now().date()
        return self.start_date <= target_date and (self.end_date is None or self.end_date >= target_date)

    def generate_bill(self, delete_old_items=True, target_date=None):
        ''' used to generate or regenerate a bill for the given target date, or
        today.  the reason old line items are generally deleted is that we want
        to make sure that a) the line item descriptions are correct, since they
        are simply strings generated from the line items themselves, and b)
        because if any fees have changed, then percentage based derivative fees
        will also change. '''

        if not target_date:
            target_date = timezone.now().date()

        period_start, period_end = self.get_period(target_date)
        if not period_start:
            return None
        logger.debug(' ')
        logger.debug('in generate_bill for target_date = %s and get_period = (%s, %s)' % (target_date, period_start, period_end))

        # a subscription's last cycle could be a pro rated one. check to see if
        # the subscription end date is before the period end; if so, change the
        # period end to be the subscription end date.
        prorated = False
        if self.end_date and self.end_date < period_end:
            prorated = True
            original_period_end = period_end
            period_end = self.end_date

        try:
            bill = SubscriptionBill.objects.get(period_start=period_start, subscription=self)
            logger.debug('Found existing bill #%d for period start %s' % (bill.id, period_start.strftime("%B %d %Y")))
            # if the bill already exists but we're updating it to be prorated,
            # we need to change the period end also.
            if prorated and bill.period_end != period_end:
                bill.period_end = period_end
                bill.save()
            # If we already have a bill and we don't want to clear out the old data
            # we can stop right here and go with the existing line items.
            if not delete_old_items:
                return list(bill.line_items)
        except Exception as e:
            logger.debug("Generating new bill item")
            bill = SubscriptionBill.objects.create(period_start=period_start, period_end=period_end)

        # Save any custom line items before clearing out the old items
        logger.debug("working with bill %d (%s)" % (bill.id, bill.period_start.strftime("%B %d %Y")))
        custom_items = list(bill.line_items.filter(custom=True))
        if delete_old_items:
            if bill.total_paid() > 0:
                logger.debug("Warning: modifying a bill with payments on it.")
            for item in bill.line_items.all():
                item.delete()

        line_items = []
        # First line item is the subscription itself.
        desc = "%s (%s to %s)" % (self.description, period_start, period_end)
        if prorated:
            period_days = Decimal((period_end - period_start).days)
            original_period_days = (original_period_end - period_start).days
            price = (period_days/original_period_days)*self.price
        else:
            price = self.price

        line_item = BillLineItem(bill=bill, description=desc, amount=price, paid_by_house=False)
        line_items.append(line_item)

        # Incorporate any custom fees or discounts. As well, track the
        # effective resource charge to be used in calculation of percentage-based
        # fees
        effective_bill_charge = price
        for item in custom_items:
            line_items.append(item)
            effective_bill_charge += item.amount  # may be negative
            logger.debug(item.amount)
        logger.debug('effective room charge after discounts: %d' % effective_bill_charge)

        # For now we are going to assume that all fees (of any kind) that are marked as "paid by house"
        # will be applied to subscriptions as well -- JLS
        for location_fee in LocationFee.objects.filter(location=self.location, fee__paid_by_house=True):
            desc = "%s (%s%c)" % (location_fee.fee.description, (location_fee.fee.percentage * 100), '%')
            amount = float(effective_bill_charge) * location_fee.fee.percentage
            logger.debug('Fee %s for %d' % (desc, amount))
            fee_line_item = BillLineItem(bill=bill, description=desc, amount=amount, paid_by_house=True, fee=location_fee.fee)
            line_items.append(fee_line_item)

        # Save this beautiful bill
        bill.save()
        for item in line_items:
            item.save()
        self.bills.add(bill)
        self.save()

        return line_items

    def generate_all_bills(self, target_date=None):
        today = timezone.now().date()

        if not target_date:
            target_date = self.start_date

        if self.end_date and self.end_date < today:
            end_date = self.end_date
        else:
            end_date = today

        period_start = target_date
        while period_start and (period_start < today) and (period_start < end_date):
            self.generate_bill(target_date=period_start)
            period_start = self.get_next_period_start(period_start)

    def last_paid(self, include_partial=False):
        ''' returns the end date of the last period with payments, unless no
        bills have been paid in which case it returns the start date of the
        first period.

        If include_partial=True we will count partially paid bills as "paid"
        '''
        bills = self.bills.order_by('period_start').reverse()
        # go backwards in time through the bills
        if not bills:
            return None
        for b in bills:
            try:
                (paid_until_start, paid_until_end) = self.get_period(target_date=b.period_end)
            except:
                logger.debug("didn't like date")
                logger.debug(b.period_end)
            if b.is_paid() or (include_partial and b.total_paid() > 0):
                return paid_until_end
        return b.period_start

    def delete_unpaid_bills(self):
        for bill in self.bills.all():
            if bill.total_paid() == 0:
                bill.delete()

    def has_unpaid_bills(self):
        for bill in self.bills.all():
            if not bill.is_paid():
                return True
        return False

    def update_for_end_date(self, new_end_date):
        ''' deletes and regenerates bills after a change in end date'''
        self.end_date = new_end_date
        self.save()

        # if the new end date is not on a period boundary, the final bill needs
        # to be pro-rated, so we need to regenerate it.
        today = timezone.localtime(timezone.now()).date()
        period_start, period_end = self.get_period(today)

        # delete unpaid bills will skip any bills with payments on them.
        self.delete_unpaid_bills()

        # in general there are SO MANY edge cases about when to regenerate
        # bills, that we just regenerate them in all cases.
        self.generate_all_bills()

    def expected_num_bills(self):
        today = timezone.localtime(timezone.now()).date()
        period_start = self.start_date
        num_expected = 0
        while period_start and (period_start < today) and (period_start < self.end_date):
            num_expected += 1
            period_start = self.get_next_period_start(period_start)
        return num_expected


class SubscriptionBill(Bill):
    period_start = models.DateField()
    period_end = models.DateField()
    subscription = models.ForeignKey(Subscription, related_name="bills", null=True)

    class Meta:
        ordering = ["-period_start"]

    def days_between(self, start, end):
        ''' return the number of days of this bill that occur between start and
        end dates'''
        days = 0
        if not self.period_end:
            # set the end date to be the end date passed in so we can work with
            # a date object, but do NOT save.
            self.period_end = end
        if self.period_start >= start and self.period_end <= end:
            days = (self.period_end - self.period_start).days
        elif self.period_start <= start and self.period_end >= end:
            days = (end - start).days
        elif self.period_start < start:
            days = (self.period_end - start).days
        elif self.period_end > end:
            days = (end - self.period_start).days
        return days


class BookingBill(Bill):
    pass


class Use(models.Model):
    ''' record of a use for a specific resource.'''

    PENDING = 'pending'
    APPROVED = 'approved'
    CONFIRMED = 'confirmed'
    HOUSE_DECLINED = 'house declined'
    USER_DECLINED = 'user declined'
    CANCELED = 'canceled'

    USE_STATUSES = (
            (PENDING, 'Pending'),
            (APPROVED, 'Approved'),
            (CONFIRMED, 'Confirmed'),
            (HOUSE_DECLINED, 'House Declined'),
            (USER_DECLINED, 'User Declined'),
            (CANCELED, 'Canceled'),
        )

    FIAT = "fiat"
    FIATDRFT = "fiatdrft"
    DRFT = "drft"
    BACKING = "backing"

    USE_ACCOUNTING = (
            (FIAT, "Fiat"),
            (FIATDRFT, "Fiat & DRFT"),
            (DRFT, "DRFT"),
            (BACKING, "Backing")
        )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, related_name='uses', null=True)
    status = models.CharField(max_length=200, choices=USE_STATUSES, default=PENDING, blank=True)
    user = models.ForeignKey(User, related_name='uses')
    arrive = models.DateField(verbose_name='Arrival Date')
    depart = models.DateField(verbose_name='Departure Date')
    arrival_time = models.CharField(help_text='Optional, if known', max_length=200, blank=True, null=True)
    resource = models.ForeignKey(Resource, null=True)
    purpose = models.TextField(verbose_name='Tell us a bit about the reason for your trip/stay')
    last_msg = models.DateTimeField(blank=True, null=True)
    accounted_by = models.CharField(max_length=200, choices=USE_ACCOUNTING, default=FIAT, blank=True)

    objects = UseManager()

    def __str__(self):
        return "%d" % self.id

    def total_nights(self):
        return (self.depart - self.arrive).days
    total_nights.short_description = "Nights"

    def drft_value(self):
        # the value of this booking in DRFT
        return self.total_nights()

    def nights_between(self, start, end):
        ''' return the number of nights of this booking that occur between
        start and end (different from total nights because the date range may
        be longer or shorter than arrive and depart dates).'''
        nights = 0
        if self.arrive >= start and self.depart <= end:
            nights = (self.depart - self.arrive).days
        elif self.arrive <= start and self.depart >= end:
            nights = (end - start).days
        elif self.arrive < start:
            nights = (self.depart - start).days
        elif self.depart > end:
            nights = (end - self.arrive).days
        return nights

    def suggest_drft(self):
        # suggest DRFT if the user has sufficient DRFT balance and the room
        # accept DRFT on these nights.
        try:
            return self.resource.drftable_between(self.arrive, self.depart) and self.user.profile.drft_spending_balance() >= self.total_nights()
        except:
            return False


class Booking(models.Model):
    ''' a model to handle the payment details related to uses'''

    class ResActionError(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    PENDING = 'pending'
    APPROVED = 'approved'
    CONFIRMED = 'confirmed'
    HOUSE_DECLINED = 'house declined'
    USER_DECLINED = 'user declined'
    CANCELED = 'canceled'

    BOOKING_STATUSES = (
            (PENDING, 'Pending'),
            (APPROVED, 'Approved'),
            (CONFIRMED, 'Confirmed'),
            (HOUSE_DECLINED, 'House Declined'),
            (USER_DECLINED, 'User Declined'),
            (CANCELED, 'Canceled'),
        )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # deprecated fields to be deleted soon ("soon")
    location_deprecated = models.ForeignKey(Location, related_name='bookings', null=True)
    status_deprecated = models.CharField(max_length=200, choices=BOOKING_STATUSES, default=PENDING, blank=True, null=True)
    user_deprecated = models.ForeignKey(User, related_name='bookings', null=True)
    arrive_deprecated = models.DateField(verbose_name='Arrival Date', null=True)
    depart_deprecated = models.DateField(verbose_name='Departure Date', null=True)
    arrival_time_deprecated = models.CharField(help_text='Optional, if known', max_length=200, blank=True, null=True)
    resource_deprecated = models.ForeignKey(Resource, null=True)
    tags_deprecated = models.CharField(max_length=200, help_text='What are 2 or 3 tags that characterize this trip?', blank=True, null=True)
    purpose_deprecated = models.TextField(verbose_name='Tell us a bit about the reason for your trip/stay', null=True)
    last_msg_deprecated = models.DateTimeField(blank=True, null=True)

    comments = models.TextField(blank=True, null=True, verbose_name='Any additional comments. (Optional)')
    rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, help_text="Uses the default rate unless otherwise specified.")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)  # the blank and null = True are artifacts of the migration JKS
    bill = models.OneToOneField(BookingBill, null=True, related_name="booking")
    suppressed_fees = models.ManyToManyField(Fee, blank=True)
    use = models.OneToOneField(Use, null=False, related_name="booking")

    @models.permalink
    def get_absolute_url(self):
        return ('booking_detail', [str(self.use.location.slug), str(self.id)])

    def generate_bill(self, delete_old_items=True, save=True, reset_suppressed=False):
        # during the booking process, we simulate a booking to generate
        # a bill and show the user what the booking would cost. in this
        # case, the booking object will not yet have a bill because it has
        # not been saved.
        booking_bill = None
        if not self.bill and save:
            self.bill = BookingBill.objects.create()
        if self.bill:
            booking_bill = self.bill

        # impt! save the custom items first or they'll be blown away when the
        # bill is regenerated.
        custom_items = []
        if booking_bill:
            custom_items = list(booking_bill.line_items.filter(custom=True))
            if delete_old_items:
                for item in booking_bill.line_items.all():
                    item.delete()

        line_items = []

        # The first line item is for the resource charge
        resource_charge_desc = "%s (%d * $%s)" % (self.use.resource.name, self.use.total_nights(), self.get_rate())
        resource_charge = self.base_value()
        resource_line_item = BillLineItem(bill=booking_bill, description=resource_charge_desc, amount=resource_charge, paid_by_house=False)
        line_items.append(resource_line_item)

        # Incorporate any custom fees or discounts
        effective_resource_charge = resource_charge
        for item in custom_items:
            line_items.append(item)
            effective_resource_charge += item.amount  # may be negative

        # A line item for every fee that applies to this location
        if reset_suppressed:
            self.suppressed_fees.clear()
        for location_fee in LocationFee.objects.filter(location=self.use.location):
            if location_fee.fee not in self.suppressed_fees.all():
                desc = "%s (%s%c)" % (location_fee.fee.description, (location_fee.fee.percentage * 100), '%')
                amount = float(effective_resource_charge) * location_fee.fee.percentage
                fee_line_item = BillLineItem(
                    bill=booking_bill, description=desc, amount=amount,
                    paid_by_house=location_fee.fee.paid_by_house, fee=location_fee.fee
                )
                line_items.append(fee_line_item)

        # Optionally save the line items to the database
        if save:
            booking_bill.save()
            for item in line_items:
                item.save()

        return line_items

    def serialize(self, include_bill=True):
        if not self.id:
            self.id = -1

        res_info = {
                'arrive': {'year': self.use.arrive.year, 'month': self.use.arrive.month, 'day': self.use.arrive.day},
                'depart': {'year': self.use.depart.year, 'month': self.use.depart.month, 'day': self.use.depart.day},
                'location': {'id': self.use.location.id, 'short_description': self.use.location.short_description, 'slug': self.use.location.slug},
                'resource': {
                    'id': self.use.resource.id, 'name': self.use.resource.name, 'description': self.use.resource.description,
                    'cancellation_policy': self.use.resource.cancellation_policy
                },
                'purpose': self.use.purpose,
                'arrival_time': self.use.arrival_time,
                'comments': self.comments,
            }

        # Now serialize the bill
        if include_bill:
            if self.bill:
                bill_line_items = self.bill.ordered_line_items()
                amount = self.bill.amount()
                total_owed = self.bill.total_owed()
            else:
                bill_line_items = self.generate_bill(delete_old_items=False, save=False)
                amount = Decimal(0.0)
                for item in bill_line_items:
                    if not item.paid_by_house:
                        amount = Decimal(amount) + Decimal(item.amount)
                total_owed = amount

            bill_info = {
                'amount': format(amount, '.2f'),
                'total_owed': format(total_owed, '.2f'),
                'ordered_line_items': [],
            }
            for item in bill_line_items:
                line_item = {
                    'paid_by_house': item.paid_by_house,
                    'description': item.description,
                    'amount': format(item.amount, '.2f'),
                }
                bill_info['ordered_line_items'].append(line_item)
            res_info['bill'] = bill_info

        return res_info

    def __str__(self):
        if self.id:
            return "booking (id = %d)" % self.id
        return "booking (unsaved)"

    def suppress_fee(self, line_item):
        logger.debug('suppressing fee')
        logger.debug(line_item.fee)
        self.suppressed_fees.add(line_item.fee)
        self.save()

    def default_rate(self):
        # default_rate always returns the default rate regardless of comps or
        # custom rates.
        return self.use.resource.default_rate

    def get_rate(self):
        if self.rate is None:
            return self.default_rate()
        return self.rate

    def base_value(self):
        # value of the booking, regardless of what has been paid
        # get_rate checks for comps and custom rates.
        return self.use.total_nights() * self.get_rate()

    def calc_non_house_fees(self):
        # Calculate the amount of fees not paid by the house
        resource_charge = self.base_value()
        amount = 0.0
        for location_fee in LocationFee.objects.filter(location=self.location):
            if not location_fee.fee.paid_by_house:
                amount = amount + (resource_charge * location_fee.fee.percentage)
        return amount

    def calc_house_fees(self):
        # Calculate the amount of fees the house owes
        resource_charge = self.base_value()
        amount = 0.0
        for location_fee in LocationFee.objects.filter(location=self.location):
            if location_fee.fee.paid_by_house:
                amount = amount + (resource_charge * location_fee.fee.percentage)
        return amount

    def calc_bill_amount(self):
        total = 0
        for item in self.generate_bill(delete_old_items=False, save=False):
            if not item.paid_by_house:
                total = total + item.amount
        return total

    def to_house(self):
        return self.base_value() - self.bill.house_fees()

    def set_rate(self, rate):
        if rate is None:
            rate = 0
        self.rate = Decimal(rate)
        self.save()
        self.generate_bill()

    def reset_rate(self):
        self.set_rate(self.use.resource.default_rate)

    def mark_last_msg(self):
        self.use.last_msg = datetime.datetime.now()
        self.use.save()

    def pending(self):
        self.use.status = Booking.PENDING
        self.use.save()

    def approve(self):
        self.use.status = Booking.APPROVED
        self.use.save()

    def confirm(self):
        self.use.status = Booking.CONFIRMED
        self.use.save()

    def cancel(self):
        # cancel this booking.
        # JKS note: we *don't* delete the bill here, because if there was a
        # refund, we want to keep it around to know how much to refund from the
        # associated fees.
        self.use.status = Booking.CANCELED
        self.use.save()

    def comp(self):
        self.set_rate(0)
        self.generate_bill()
        self.save()

    def is_paid(self):
        return self.bill.total_owed() <= 0

    def is_comped(self):
        return self.rate == 0

    def is_pending(self):
        return self.use.status == Booking.PENDING

    def is_approved(self):
        return self.use.status == Booking.APPROVED

    def is_confirmed(self):
        return self.use.status == Booking.CONFIRMED

    def is_canceled(self):
        return self.use.status == Booking.CANCELED

    def payments(self):
        return self.bill.payments.all()

    def non_refund_payments(self):
        return self.bill.payments.filter(paid_amount__gt=0)


@receiver(pre_save, sender=Booking)
def booking_create_bill(sender, instance, **kwargs):
    # create a new bill object if the booking does not already have one.
    if not instance.bill:
        bill = BookingBill.objects.create()
        instance.bill = bill


class PaymentManager(models.Manager):
    def booking_payments_by_location(self, location):
        booking_payments = Payment.objects.filter(bill__in=BookingBill.objects.filter(booking__use__location=location))
        return booking_payments

    def subscription_payments_by_location(self, location):
        subscription_payments = Payment.objects.filter(bill__in=SubscriptionBill.objects.filter(subscription__location=location))
        return subscription_payments

    def booking_payments_by_resource(self, resource):
        booking_payments = Payment.objects.filter(bill__in=BookingBill.objects.filter(booking__use__resource=resource))
        return booking_payments


class Payment(models.Model):
    bill = models.ForeignKey(Bill, related_name="payments", null=True)
    user = models.ForeignKey(User, related_name="payments", null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_service = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Stripe, Paypal, Dwolla, etc. May be empty")
    payment_method = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Visa, cash, bank transfer")
    paid_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    last4 = models.IntegerField(null=True, blank=True)

    objects = PaymentManager()

    def __str__(self):
        return "%s: %s - $%s" % (str(self.payment_date)[:16], self.user, self.paid_amount)

    def to_house(self):
        return self.paid_amount - self.non_house_fees() - self.house_fees()

    def is_refund(self):
        return self.paid_amount < 0

    def refund_payments(self):
        payments = Payment.objects.filter(transaction_id=self.transaction_id)
        refunds = []
        for p in payments:
            if p.is_refund():
                refunds.append(p)
        logger.debug(refunds)
        return refunds

    def net_paid(self):
        # manual/cash transactions will not have a transaction id. this feels a
        # bit fragile but probably the best we can do with this data structure?
        if self.transaction_id == "Manual":
            return self.paid_amount
        payments = Payment.objects.filter(transaction_id=self.transaction_id)
        balance = 0
        for p in payments:
            balance += p.paid_amount
        return balance

    def is_fully_refunded(self):
        balance = self.net_paid()
        if balance > 0:
            return False
        return True

    def non_house_fees(self):
        ''' returns the absolute amount of the user paid (non-house) fee(s) '''
        # takes the appropriate bill line items and applies them proportionately to the payment.
        fee_line_items_not_paid_by_house = self.bill.line_items.filter(fee__isnull=False).filter(paid_by_house=False)
        subtotal = self.bill.subtotal_amount()
        non_house_fee_on_payment = Decimal(0.0)
        # this payment may or may not represent the entire bill amount. we need
        # to know what fraction of the total bill amount it was so that we can
        # apply the fees proportionately to the payment amount. note: in many
        # cases, the fraction will be 1.

        if self.bill.amount() == 0:
            fraction = 0
        else:
            fraction = self.paid_amount/self.bill.amount()

        fractional_base_amount = subtotal * fraction
        for line_item in fee_line_items_not_paid_by_house:
                # JKS important! this assumes that the line item value accurately
                # reflects the fee percentage. this should be true, but technically
                # could be edited in the admin page to be anything. do we want to
                # enforce this?
            non_house_fee_on_payment += fractional_base_amount * Decimal(line_item.fee.percentage)

        return non_house_fee_on_payment

    def house_fees(self):
        # takes the appropriate bill line items and applies them proportionately to the payment.
        fee_line_items_paid_by_house = self.bill.line_items.filter(paid_by_house=True)
        subtotal = self.bill.subtotal_amount()
        house_fee_on_payment = Decimal(0.0)
        # this payment may or may not represent the entire bill amount. we need
        # to know what fraction of the total bill amount it was so that we can
        # apply the fees proportionately to the payment amount. note: in many
        # cases, the fraction will be 1.
        if self.bill.amount() == 0:
            fraction = 0
        else:
            fraction = self.paid_amount/self.bill.amount()
        fractional_base_amount = subtotal * fraction
        for line_item in fee_line_items_paid_by_house:
            # JKS important! this assumes that the line item value accurately
            # reflects the fee percentage. this should be true, but technically
            # could be edited in the admin page to be anything. do we want to
            # enforce this?
            house_fee_on_payment += fractional_base_amount * Decimal(line_item.fee.percentage)
        return house_fee_on_payment


def profile_img_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # rename file to random string
    filename = "%s.%s" % (uuid.uuid4(), ext.lower())

    upload_path = "avatars/%s/" % instance.user.username
    upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    if not os.path.exists(upload_abs_path):
        os.makedirs(upload_abs_path)
    return os.path.join(upload_path, filename)


class UserProfile(models.Model):
    # User model fields: username, first_name, last_name, email,
    # password, is_staff, is_active, is_superuser, last_login, date_joined,
    user = models.OneToOneField(User, related_name='profile')
    updated = models.DateTimeField(auto_now=True)
    image = ProcessedImageField(
        upload_to=profile_img_upload_to,
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90})
    image_thumb = ImageSpecField(
        source='image',
        processors=[ResizeToFill(150, 150)],
        format='JPEG',
        options={'quality': 90})
    bio = models.TextField("About you", blank=True, null=True)
    links = models.TextField(help_text="Comma-separated", blank=True, null=True)
    phone = models.CharField(
        "Phone Number", max_length=20, blank=True, null=True,
        help_text="Optional. Most locations operate primarily by email, but a phone number can be helpful for last " +
                  "minute coordination and the unexpected."
    )

    projects = models.TextField(verbose_name='Current Projects', help_text='Describe one or more projects you are currently working on')
    sharing = models.TextField(help_text="Is there anything you'd be interested in learning or sharing during your stay?")
    discussion = models.TextField(
        help_text="We like discussing thorny issues with each other. What's a question that's been on your mind lately " +
                  "that you don't know the answer to?"
    )
    referral = models.CharField(max_length=200, help_text='How did you hear about us? (Give a name if possible!)')
    city = models.CharField(max_length=200, verbose_name="City", help_text="In what city are you primarily based?")
    # currently used to store the stripe customer id but could be used for
    # other payment platforms in the future
    customer_id = models.CharField(max_length=200, blank=True, null=True)
    # JKS TODO between last4 and the customer_id, payment methods should really be their own model.
    last4 = models.IntegerField(null=True, blank=True, help_text="Last 4 digits of the user's card on file, if any")
    primary_accounts = models.ManyToManyField(Account, help_text="one for each currency", related_name="primary_for", blank=True)

    def __str__(self):
        return str(self.user)

    def get_or_create_primary_account(self, currency):
        # the prumary account should be unique for each currency (enforced by
        # the m2m_changed receiver), but it migh tbe None, and get() throws an
        # error if that's the case. Hence filter().first().
        logger.debug('checking for primary account...')
        primary = self.primary_accounts.filter(currency=currency).first()
        if primary:
            logger.debug("found: %s (id %d)" % (primary, primary.id))
        if not primary:
            primary = Account(currency=currency, name="%s %s Account (primary)" % (self.user.first_name, currency.name))
            primary.save()
            primary.owners.add(self.user)
            logger.debug('saving new primary account')
            logger.debug(primary.id)
            self.primary_accounts.add(primary)
        return primary

    def _has_primary_drft_account(self):
        return self.primary_accounts.filter(currency=Currency.objects.get(name="DRFT")).first()

    def primary_drft_account(self):
        return self.get_or_create_primary_account(currency=Currency.objects.get(name="DRFT"))

    def drft_spending_balance(self):
        # returns balance from primary account only. the thesis is that users
        # should move balances INTO their primary account to spend it.
        account = self.get_or_create_primary_account(currency=Currency.objects.get(name="DRFT"))
        return account.get_balance()

    def accounts(self):
        return list(self.user.accounts_owned.all()) + list(self.user.accounts_administered.all())

    def accounts_in_currency(self, currency):
        return list(self.user.accounts_owned.filter(currency=currency)) + list(self.user.accounts_administered.filter(currency=currency))


# FIXME: this should use related_name
User.rooms_backed = (lambda u: Resource.objects.backed_by(user=u))
# FIXME: nope. explicit ordering everywhere.
User._meta.ordering = ['username']


# Note: primary.accounts.'through' is django's name for the M2M class
@receiver(m2m_changed, sender=UserProfile.primary_accounts.through)
def primary_accounts_changed(sender, action, instance, reverse, pk_set, **kwargs):
    logger.debug('p2p_changed signal')
    logger.debug(action)
    if action == "pre_add":
        logger.debug(instance)  # should be a UserProfile unless reversed

        # since the sender is defined as UserProfile in the @receiver line,
        # UserProfile is the forward relation and Account is the reverse relation
        if reverse:  # Account.primary_for.add(...)
            account = instance
        else:  # UserProfile.primary_accounts.add(...)
            user_profile = instance

        for pk in pk_set:
            # multiple objects can be add()-ed at once, and those objects will be
            # of type Account or UserProfile depending on whether this is a forward
            # or reverse relationship.
            if reverse:
                user_profile = UserProfile.objects.get(pk)
            else:
                account = Account.objects.get(pk=pk)

            # uniqueness constraint: one primary account per currency
            assert not user_profile.primary_accounts.filter(currency=account.currency)
            # ensure user is an owner of primary account
            assert user_profile.user in account.owners.all()


class EmailTemplate(models.Model):
    ''' Templates for the typical emails sent by administrators of the system.
    The from-address is usually set from the location settings,
    and the recipients are determined by the action and booking in question. '''

    SUBJECT_PREFIX = settings.EMAIL_SUBJECT_PREFIX
    FROM_ADDRESS = settings.DEFAULT_FROM_EMAIL

    BOOKING = 'booking'
    SUBSCRIPTION = 'subscription'
    context_options = (
        (BOOKING, 'Booking'),
        (SUBSCRIPTION, 'Subscription')
    )

    body = models.TextField(verbose_name="The body of the email")
    subject = models.CharField(max_length=200, verbose_name="Default Subject Line")
    name = models.CharField(max_length=200, verbose_name="Template Name")
    creator = models.ForeignKey(User)
    shared = models.BooleanField(default=False)
    context = models.CharField(max_length=32, choices=context_options, blank=False, null=False)

    def __str__(self):
        return self.name


class LocationEmailTemplate(models.Model):
    ''' Location Template overrides for system generated emails '''

    ADMIN_DAILY = 'admin_daily_update'
    GUEST_DAILY = 'guest_daily_update'
    INVOICE = 'invoice'
    RECEIPT = 'receipt'
    SUBSCRIPTION_RECEIPT = 'subscription_receipt'
    NEW_BOOKING = 'newbooking'
    WELCOME = 'pre_arrival_welcome'
    DEPARTURE = 'departure'

    KEYS = (
            (ADMIN_DAILY, 'Admin Daily Update'),
            (GUEST_DAILY, 'Guest Daily Update'),
            (INVOICE, 'Invoice'),
            (RECEIPT, 'Booking Receipt'),
            (SUBSCRIPTION_RECEIPT, 'Subscription Receipt'),
            (NEW_BOOKING, 'New Booking'),
            (WELCOME, 'Pre-Arrival Welcome'),
            (DEPARTURE, 'Departure'),
        )

    location = models.ForeignKey(Location)
    key = models.CharField(max_length=32, choices=KEYS)
    text_body = models.TextField(verbose_name="The text body of the email")
    html_body = models.TextField(blank=True, null=True, verbose_name="The html body of the email")


class LocationFee(models.Model):
    location = models.ForeignKey(Location)
    fee = models.ForeignKey(Fee)

    def __str__(self):
        return '%s: %s' % (self.location, self.fee)


class BillLineItem(models.Model):
    bill = models.ForeignKey(Bill, related_name="line_items", null=True)
    # the fee that this line item was based on, if any (line items are also
    # generated for the base resource rate, which doesn't have an associated fee)
    fee = models.ForeignKey(Fee, null=True)
    description = models.CharField(max_length=200)
    # the actual amount of this line item (if this is a line item derived from
    # a fee, generally it will be the fee amount but, technically, not
    # necessarily)
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    paid_by_house = models.BooleanField(default=True)
    custom = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class LocationMenu(models.Model):
    location = models.ForeignKey(Location)
    name = models.CharField(
        max_length=15,
        help_text="A short title for your menu. Note: If there is only one page in the menu, it will be used as a " +
                  "top level nav item, and the menu name will not be used."
    )

    def page_count(self):
        return len(self.pages.all())

    def __str__(self):
        return self.name


class LocationFlatPage(models.Model):
    menu = models.ForeignKey(
        LocationMenu, related_name="pages",
        help_text="Note: If there is only one page in the menu, it will be used as a top level nav item, and the menu name will not be used."
    )
    flatpage = models.OneToOneField(FlatPage)

    def slug(self):
        url = self.flatpage.url
        u_split = url.split('/')
        if len(u_split) > 3:
            return u_split[3]
        return None

    def title(self):
        return self.flatpage.title

    def content(self):
        return self.flatpage.content

    def __str__(self):
        return self.flatpage.title


class UserNote(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True)
    user = models.ForeignKey(User, blank=False, null=False, related_name="user_notes")
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return '%s - %s: %s' % (self.created.date(), self.user.username, self.note)


class UseNote(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True)
    booking_deprecated = models.ForeignKey(Booking, blank=True, null=True, related_name="booking_notes")
    use = models.ForeignKey(Use, blank=False, null=False, related_name="use_notes")
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return '%s - %d: %s' % (self.created.date(), self.booking.id, self.note)


class SubscriptionNote(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True)
    subscription = models.ForeignKey(Subscription, blank=False, null=False, related_name="communitysubscription_notes")
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return '%s - %d: %s' % (self.created.date(), self.subscription.id, self.note)


class CapacityChangeManager(models.Manager):
    def _latest_change(self, date, resource):
        return self.get_queryset().filter(resource=resource).filter(start_date__lte=date).order_by('-start_date').first()

    def _next_capacity(self, capacity):
        return self.get_queryset().filter(resource=capacity.resource).filter(start_date__gt=capacity.start_date).order_by('start_date').first()

    def _previous_capacity(self, capacity):
        return self.get_queryset().filter(resource=capacity.resource).filter(start_date__lt=capacity.start_date).order_by('-start_date').first()

    def delete_next_quantity(self, capacity):
        self._next_capacity(capacity).delete()

    def drft_on(self, date, resource):
        latest_change = self._latest_change(date, resource)
        if latest_change:
            return latest_change.accept_drft
        else:
            return False

    def quantity_on(self, date, resource):
        latest_change = self._latest_change(date, resource)
        if latest_change:
            return latest_change.quantity
        else:
            return 0

    def would_not_change_previous_quantity(self, capacity):
        previous_capacity = self._previous_capacity(capacity)
        if not previous_capacity:
            return False
        return (
            previous_capacity.quantity == capacity.quantity
            and previous_capacity.accept_drft == capacity.accept_drft
        )

    def same_as_next_quantity(self, capacity):
        next_capacity = self._next_capacity(capacity)
        if not next_capacity:
            return False
        return (
            next_capacity.quantity == capacity.quantity
            and next_capacity.accept_drft == capacity.accept_drft
        )


class CapacityChange(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    resource = models.ForeignKey(Resource, related_name="capacity_changes")
    start_date = models.DateField()
    quantity = models.IntegerField()
    accept_drft = models.BooleanField(default=False)
    objects = CapacityChangeManager()

    class Meta:
        unique_together = ('start_date', 'resource',)


class BackingManager(models.Manager):
    def by_user(self, user):
        return self.get_queryset().filter(money_account__owners=user)

    def setup_new(self, resource, backers, start):
        b = Backing(resource=resource, start=start)
        assert b.comes_after_others()
        b._setup_accounts(backers)
        b.save()
        b.users.add(*backers)
        b.money_account.name = "%s USD Account: Backing %d " % (b.resource, b.pk)
        b.money_account.save()
        b.drft_account.name = "%s DRFT Account: Backing %d " % (b.resource, b.pk)
        b.drft_account.save()
        return b


class Backing(models.Model):
    resource = models.ForeignKey(Resource, related_name='backings')
    money_account = models.ForeignKey(Account, related_name='+')
    drft_account = models.ForeignKey(Account, related_name='+')
    subscription = models.ForeignKey(Subscription, blank=True, null=True)
    users = models.ManyToManyField(User, related_name="backings")
    start = models.DateField(default=django.utils.timezone.now)
    end = models.DateField(blank=True, null=True)
    objects = BackingManager()

    def __str__(self):
        return "Backing %d for %s" % (self.pk, self.resource)

    def next_backing(self):
        return Backing.objects.filter(resource=self.resource).filter(start__gt=self.start).order_by('start').first()

    def previous_backing(self):
        return Backing.objects.filter(resource=self.resource).filter(start__lt=self.start).order_by('-start').first()

    def comes_after_others(self):
        ''' checks that this backing comes strictly after any other for this
        resource. '''

        # any other backing for this resource without an end date, period
        if Backing.objects.filter(resource=self.resource, end=None).exclude(pk=self.pk):
            logger.debug('backing without end date')
            return False
        # start date in past, end date after self.start
        if Backing.objects.filter(resource=self.resource, start__lte=self.start, end__gt=self.start).exclude(pk=self.pk):
            logger.debug('start date in past, end date after start:')
            logger.debug(self.start)
            logger.debug(Backing.objects.filter(resource=self.resource, start__lte=self.start, end__gt=self.start).exclude(pk=self.pk))
            return False
        # any backing for this resource with a start date in the future
        if Backing.objects.filter(resource=self.resource, start__gt=self.start):
            logger.debug('another backing has a start date in the future')
            return False
        return True

    def _setup_accounts(self, backers):
        # ensure we are not overwriting existing accounts
        assert not hasattr(self, 'money_account') and not hasattr(self, 'drft_account')
        # create accounts for this backing
        usd, _ = Currency.objects.get_or_create(name="USD", defaults={'symbol': '$'})
        ma = Account.objects.create(
            currency=usd,
            name="%s Backing USD Account" % self.resource,
            type=Account.CREDIT
        )
        ma.owners.add(*backers)
        self.money_account = ma

        drft, _ = Currency.objects.get_or_create(name='DRFT', defaults={'symbol': 'Ɖ'})
        da = Account.objects.create(
            currency=drft,
            name="%s Backing DRFT Account" % self.resource,
            type=Account.CREDIT)
        da.owners.add(*backers)
        self.drft_account = da


class HouseAccount(models.Model):
    location = models.ForeignKey(Location)
    account = models.ForeignKey(Account)


class UseTransaction(models.Model):
    use = models.ForeignKey(Use)
    transaction = models.ForeignKey(Transaction)

    def __str__(self):
        return "Transaction %d <> Use %d" % (self.transaction.id, self.use.id)
