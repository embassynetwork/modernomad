from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import render
from django.db import transaction
from PIL import Image
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from core.forms import ReservationForm, AdminReservationForm, UserProfileForm, SubscriptionEmailTemplateForm, ReservationEmailTemplateForm, PaymentForm, AdminSubscriptionForm
from core.forms import LocationSettingsForm, LocationUsersForm, LocationContentForm, LocationPageForm, LocationMenuForm, LocationRoomForm, LocationReservableForm
from django.core import urlresolvers
from django.contrib import messages
from django.conf import settings
from core.decorators import house_admin_required, resident_or_admin_required
from django.db.models import Q
from core.models import *
from core.tasks import guest_welcome
from core import payment_gateway
import uuid, base64, os
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from gather.tasks import published_events_today_local, events_pending
from gather.models import Event
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import time
import json, datetime, stripe
from django.http import JsonResponse
from reservation_calendar import GuestCalendar
from emails import send_reservation_receipt, send_subscription_receipt, new_reservation_notify, updated_reservation_notify, send_from_location_address, admin_new_subscription_notify, subscription_note_notify
from django.core.urlresolvers import reverse
from core.models import get_location
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.core.serializers.json import DateTimeAwareJSONEncoder
import logging
from django.views.decorators.csrf import csrf_exempt
import csv
from django.http import Http404
from core.data_fetchers import SerializedRoomAvailability
from core.data_fetchers import SerializedNullRoomAvailability

logger = logging.getLogger(__name__)

def location(request, location_slug):
	try:
		location = Location.objects.get(slug=location_slug)
		print location.get_members()
		print '--'
		print request.user

		if location.visibility == 'public' or location.visibility == 'link':
			has_permission = True
		elif request.user in location.get_members():
			has_permission = True
		else:
			has_permission = False

		if not has_permission:
			raise Location.DoesNotExist

	except Location.DoesNotExist:
		raise Http404("The location does not exist or you do not have permission to view it")

	return render(request, "landing.html", {'location': location})

def guest_rooms(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	rooms = location.guest_rooms()
	return render(request, "location_rooms.html", {'rooms': rooms, 'location': location})

def view_room(request, location_slug, room_id):
	location = get_object_or_404(Location, slug=location_slug)
	room = get_object_or_404(Resource, id=room_id)
	today = timezone.localtime(timezone.now())
	month = request.GET.get("month")
	year = request.GET.get("year")
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	return render(request, "room.html", {'room': room, 'location': location, "next_month": next_month, "prev_month": prev_month})

def community(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	residents = location.residents.all()
	return render(request, "location_community.html", {'residents': residents, 'location': location})

def team(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	team = location.house_admins.all()
	return render(request, "location_team.html", {'team': team, 'location': location})

def guests(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	guests_today = location.guests_today()
	return render(request, "location_guests.html", {'guests': guests_today, 'location': location})

def projects(request, location_slug):
	pass

def get_calendar_dates(month, year):
	if month:
		month = int(month)
	else:
		month = datetime.date.today().month
	if year:
		year = int(year)
	else:
		year = datetime.date.today().year

	# start date is first day of the month
	start = datetime.date(year,month,1)
	# calculate end date by subtracting one day from the start of the next
	# month (saves us from having to reference how many days that month has)
	next_month = (month+1) % 12
	if next_month == 0: next_month = 12
	if next_month < month:
		next_months_year = year + 1
	else: next_months_year = year
	end = datetime.date(next_months_year, next_month, 1)
	next_month = end # for clarity

	# also calculate the previous month for reference in the template
	prev_month = (month-1) % 12
	if prev_month == 0: prev_month = 12
	if prev_month > month:
		prev_months_year = year - 1
	else: prev_months_year = year
	prev_month = datetime.date(prev_months_year, prev_month, 1)

	# returns datetime objects (start, end, next_month, prev_month) and ints (month, year)
	return start, end, next_month, prev_month, month, year

def today(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	# get all the reservations that intersect today (including those departing
	# and arriving today)
	today = timezone.now()
	reservations_today = Reservation.objects.filter(Q(status="confirmed") | Q(status="approved")).exclude(depart__lt=today).exclude(arrive__gt=today)
	guests_today = []
	for r in reservations_today:
		guests_today.append(r.user)
	residents = location.residents.all()
	people_today = guests_today + list(residents)

	events_today = published_events_today_local(location)
	return render(request, "today.html", {'people_today': people_today, 'events_today': events_today})

def room_occupancy_month(room, month, year):
	print room, month, year
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	# note the day parameter is meaningless
	report_date = datetime.date(year, month, 1)
	reservations = Reservation.objects.filter(resource=room).filter(status="confirmed").exclude(depart__lt=start).exclude(arrive__gt=end)

	# payments *received* this month for this room
	payments_for_room = Payment.objects.reservation_payments_by_resource(room).filter(payment_date__gte=start).filter(payment_date__lte=end)
	payments_cash = 0
	for p in payments_for_room:
		payments_cash += p.paid_amount

	nights_available = 0
	nights_occupied = 0
	payments_accrual = 0
	outstanding_value = 0
	partial_paid_reservations = []
	total_comped_nights = 0
	total_comped_value = 0


	# not calculating:
	# payments this month for previous months
	# payments for this month FROM past months (except inasmuch as its captured in the payments_accrual)

	# iterate over the reservables to calculate how many nights the room was
	# actually available.
	room_reservables = room.reservables.all()
	for reservable in room_reservables:
		if not reservable.end_date:
			# XXX account for reservables without end date by temporarily
			# setting the end date to be the end of the month.  IMPT: do
			# NOT save this. it's a temporary hack so that we can work with
			# end dates.
			reservable.end_date = end

		if reservable.end_date < start or reservable.start_date > end:
			# no reservable dates in this month
			continue
		if reservable.start_date < start:
			start_reservable = start
		else:
			start_reservable = reservable.start_date
		if reservable.end_date > end:
			end_reservable = end
		else:
			end_reservable = reservable.end_date
		nights_available += (end_reservable - start_reservable).days
	if room.shared:
		nights_available *= room.beds

	# cash for room this month

	# occupancy for room this month
	for r in reservations:
		comp = False
		partial_payment = False
		total_owed = 0.0

		# in case this reservation crossed a month boundary, first calculate
		# nights of this reservation that took place this month
		if r.arrive >=start and r.depart <= end:
			nights_this_month = (r.depart - r.arrive).days
		elif r.arrive <=start and r.depart >= end:
			nights_this_month = (end - start).days
		elif r.arrive < start:
			nights_this_month = (r.depart - start).days
		elif r.depart > end:
			nights_this_month = (end - r.arrive).days

		# if it's the first of the month and the person left on the 1st, then
		# that's actually 0 days this month which we don't need to include.
		if nights_this_month == 0:
			continue

		nights_occupied += nights_this_month

		# XXX Note! get_rate() returns the base rate, but does not incorporate
		# any discounts. so we use subtotal_amount here.
		rate = r.bill.subtotal_amount()/r.total_nights()

		if r.is_comped():
			total_comped_nights += nights_this_month
			total_comped_value += nights_this_month*r.default_rate()
			comp = True
			unpaid = False
		else:
			# XXX todo do we want to check if a res is fully paid vs.just
			# existence of payments? if it's partially paid what is the desired
			# behavior.
			if r.payments():
				paid_rate = r.bill.to_house() / r.total_nights()
				payments_accrual += nights_this_month*paid_rate

			# if a reservation rate is set to 0 is automatically gets counted as a comp
			if r.bill.total_owed() > 0:
				outstanding_value += r.bill.total_owed()
				partial_paid_reservations.append(r.id)

	params = [month, year, round(payments_cash, 2), round(payments_accrual, 2), nights_occupied, nights_available, partial_paid_reservations, total_comped_nights, round(total_comped_value, 2)]
	return params

@resident_or_admin_required
def room_occupancy(request, location_slug, room_id, year):
	room = get_object_or_404(Resource, id=room_id)
	year = int(year)
	response = HttpResponse(content_type='text/csv')
	output_filename = "%s Occupancy Report %d.csv" % (room.name, year)
	response['Content-Disposition'] = 'attachment; filename=%s' % output_filename
	writer = csv.writer(response)
	if room.location.slug != location_slug:
		writer.writerow(["invalid room",])
		return response

	writer.writerow([str(year) + " Report for " + room.name,])
	writer.writerow(['Month', 'Year', 'Payments Cash', 'Payments Accrual', 'Nights Occupied', 'Nights Available', 'Partial Paid Reservations', 'Comped Nights', 'Comped Value'])
	# we don't have data before 2012 or in the future
	if (year < 2012) or (year > datetime.date.today().year):
		return response

	for month in range(1,13):
		params = room_occupancy_month(room, month, year)
		writer.writerow(params)

	return response

def monthly_occupant_report(location_slug, year, month):
	location = get_object_or_404(Location, slug=location_slug)
	today = datetime.date.today()
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	occupants = {}
	occupants['residents'] = {}
	occupants['guests'] = {}
	occupants['members'] = {}
	messages = []

	# calculate datas for people this month (as relevant), including: name, email, total_nights, total_value, total_comped, owing, and reference ids
	for user in location.residents.all():
		if user in occupants['residents'].keys():
			messages.append("user %d (%s %s) showed up in residents list twice. this shouldn't happen. the second instance was skipped." % (user.id, user.first_name, user.last_name))
		else:
			occupants['residents'][user] = {'name': user.get_full_name(), 'email': user.email, 'total_nights': (end - start).days}

	reservations = Reservation.objects.filter(location=location).filter(status="confirmed").exclude(depart__lt=start).exclude(arrive__gt=end)
	for r in reservations:
		nights_this_month = r.nights_between(start, end)
		u = r.user
		comped_nights_this_month = 0
		owing = []
		effective_rate = r.bill.subtotal_amount()/r.total_nights()
		value_this_month = nights_this_month*effective_rate
		if r.is_comped():
			comped_nights_this_month = nights_this_month
		if r.bill.total_owed() > 0:
			owing.append(r.id)

		# now assemble it all
		if u not in occupants['guests'].keys():
			occupants['guests'][u] = {
				'name': u.get_full_name(),
				'email': u.email,
				'total_nights': nights_this_month,
				'total_value': value_this_month,
				'total_comped': comped_nights_this_month,
				'owing': owing,
				'ids': [r.id,]
				}
		else:
			occupants['guests'][u]['total_nights'] += nights_this_month
			occupants['guests'][u]['total_value'] += value_this_month
			occupants['guests'][u]['total_comped'] += comped_nights_this_month
			if owing:
				occupants['guests'][u]['owing'].append(owing)
			occupants['guests'][u]['ids'].append(r.id)

	# check for subscriptions that were active for any days this month.
	subscriptions = list(Subscription.objects.active_subscriptions_between(start, end).filter(location=location))
	for s in subscriptions:
		days_this_month = s.days_between(start, end)
		u = s.user
		comped_days_this_month = 0
		owing = None
		# for subscriptions, the 'value' is the sum of the effective daily rate
		# associated with the days of the bill(s) that occurred this month.
		bills_between = s.bills_between(start, end)
		value_this_month = 0
		for b in bills_between:
			effective_rate= b.subtotal_amount()/(b.period_end - b.period_start).days
			value_this_bill_this_month = effective_rate*b.days_between(start, end)
			value_this_month += value_this_bill_this_month

			# also make a note if this subscription has any bills that have an
			# outstanding balance. we store the subscription not the bill,
			# since that's the way an admin would view it from the website, so
			# check for duplicates since there could be multiple unpaid but we
			# still are pointing people to the same subscription.
			if b.total_owed() > 0:
				if not owing:
					owing = b.subscription.id

			if b.amount() == 0:
				comped_days_this_month += b.days_between(start, end)

		# ok now asssemble the dicts!
		if u not in occupants['members'].keys():
			occupants['members'][u] = {
				'name': u.get_full_name(),
				'email': u.email,
				'total_nights': days_this_month,
				'total_value': value_this_month,
				'total_comped': comped_days_this_month,
				'owing': [owing,],
				'ids': [s.id,]
				}
		else:
			occupants['members'][u]['total_nights'] += nights_this_month
			occupants['members'][u]['total_value'] += value_this_month
			occupants['members'][u]['total_comped'] += comped_nights_this_month
			if owing:
				occupants['members'][u]['owing'].append(owing)
			occupants['members'][u]['ids'].append(s.id)

	messages.append('If a membership has a weird total_value, it is likely because there was a discount or fee applied to an individual bill. Check the membership page.')
	return occupants, messages

@resident_or_admin_required
def occupancy(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	today = datetime.date.today()
	month = request.GET.get("month")
	year = request.GET.get("year")

	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	# note the day parameter is meaningless
	report_date = datetime.date(year, month, 1)
	reservations = Reservation.objects.filter(location=location).filter(status="confirmed").exclude(depart__lt=start).exclude(arrive__gt=end)

	person_nights_data = []
	total_occupied_person_nights = 0
	total_income = 0
	total_comped_nights = 0
	total_comped_income = 0
	total_shared_nights = 0
	total_private_nights = 0
	unpaid_total = 0
	room_income = {}
	room_occupancy = {}
	income_for_this_month = 0
	income_for_future_months = 0
	income_from_past_months = 0
	income_for_past_months = 0
	paid_rate_discrepancy = 0
	payment_discrepancies = []
	paid_amount_missing = []
	room_income_occupancy = {}
	total_available_person_nights = 0
	overall_occupancy = 0

	# JKS note: this section breaks down income by whether it is income for this
	# month, for future months, from past months, for past months, for this
	# month, etc... but it turns out that this gets almost impossible to track
	# because there's many edge cases causd by reservations being edited,
	# appended to, partial refunds, etc. so, it's kind of fuzzy. if you try and
	# work on it, don't say i didn't warn you :).

	payments_this_month = Payment.objects.reservation_payments_by_location(location).filter(payment_date__gte=start).filter(payment_date__lte=end)
	for p in payments_this_month:
		r = p.bill.reservationbill.reservation
		nights_before_this_month = datetime.timedelta(0)
		nights_after_this_month = datetime.timedelta(0)
		if r.arrive < start and r.depart < start:
			# all nights for this reservation were in a previous month
			nights_before_this_month = (r.depart - r.arrive)

		elif r.arrive < start and r.depart <= end:
			# only nights before and during this month, but night for this
			# month are calculated below so only tally the nights for before
			# this month here.
			nights_before_this_month = (start - r.arrive)

		elif r.arrive >= start and r.depart <= end:
			# only nights this month, don't need to calculate this here because
			# it's calculated below.
			continue

		elif r.arrive >= start and r.arrive <= end and r.depart > end:
			# some nights are after this month
			nights_after_this_month = (r.depart - end)

		elif r.arrive > end:
			# all nights are after this month
			nights_after_this_month = (r.depart - r.arrive)

		elif r.arrive < start and r.depart > end:
			# there are some days paid for this month that belong to the previous month
			nights_before_this_month = (start - r.arrive)
			nights_after_this_month = (r.depart - end)

		# in the event that there are multiple payments for a reservation, this
		# will basically amortize each payment across all nights
		income_for_future_months += nights_after_this_month.days*(p.to_house()/(r.depart - r.arrive).days)
		income_for_past_months += nights_before_this_month.days*(p.to_house()/(r.depart - r.arrive).days)

	for r in reservations:
		comp = False
		partial_payment = False
		total_owed = 0.0

		nights_this_month = r.nights_between(start, end)
		# if it's the first of the month and the person left on the 1st, then
		# that's actually 0 days this month which we don't need to include.
		if nights_this_month == 0:
			continue

		# XXX Note! get_rate() returns the base rate, but does not incorporate
		# any discounts. so we use subtotal_amount here.
		rate = r.bill.subtotal_amount()/r.total_nights()
		if r.is_comped():
			total_comped_nights += nights_this_month
			total_comped_income += nights_this_month*r.default_rate()
			comp = True
			unpaid = False
		else:
			this_room_occupancy = room_occupancy.get(r.resource, 0)
			this_room_occupancy += nights_this_month
			room_occupancy[r.resource] = this_room_occupancy

			# the bill has the amount that goes to the house after fees
			to_house_per_night = r.bill.to_house()/r.total_nights()
			total_income += nights_this_month*to_house_per_night
			this_room_income = room_income.get(r.resource, 0)
			this_room_income += nights_this_month*to_house_per_night
			room_income[r.resource] = this_room_income

			# If there are payments, calculate the payment rate
			if r.payments():
				paid_rate = (r.bill.total_paid() - r.bill.non_house_fees()) / r.total_nights()
				if paid_rate != rate:
					logger.debug("reservation %d has paid rate = $%d and rate set to $%d" % (r.id, paid_rate, rate))
					paid_rate_discrepancy += nights_this_month * (paid_rate - rate)
					payment_discrepancies.append(r.id)

			# JKS this section tracks whether payment for this reservation
			# were made in a prior month or in this month.
			if r.is_paid():
				for p in r.payments():
					if p.payment_date.date() < start:
						income_from_past_months += nights_this_month*(p.to_house()/(r.depart - r.arrive).days)
					# if the payment was sometime this month, we account for
					# it. if it was in a future month, we'll show it as "income
					# for previous months" in that month. we skip it here.
					elif p.payment_date.date() <= end:
						income_for_this_month += nights_this_month*(p.to_house()/(r.depart - r.arrive).days)
					unpaid = False
			else:
				unpaid_total += (to_house_per_night*nights_this_month)
				unpaid = True
				if r.bill.total_owed() < r.bill.amount():
					partial_payment = True
					total_owed = r.bill.total_owed()

		person_nights_data.append({
			'reservation': r,
			'nights_this_month': nights_this_month,
			'room': r.resource.name,
			'rate': rate,
			'partial_payment': partial_payment,
			'total_owed': total_owed,
			'total': nights_this_month*rate,
			'comp': comp,
			'unpaid': unpaid
		})
		total_occupied_person_nights += nights_this_month

	rooms_with_availability_this_month = []
	location_rooms = location.resources.all()
	total_reservable_days = 0
	reservable_days_per_room = {}
	for room in location_rooms:
		room_reservables = room.reservables.all()
		reservable_days_this_room = 0
		for reservable in room_reservables:
			if not reservable.end_date:
				# XXX  account for reservables without end date by temporarily
				# setting the end date to be the end of the month.  IMPT: do
				# NOT save this. it's a temporary hack so that we can work with
				# end dates.
				reservable.end_date = end

			if reservable.end_date < start or reservable.start_date > end:
				# no reservable dates in this month
				continue
			if reservable.start_date < start:
				start_reservable = start
			else:
				start_reservable = reservable.start_date
			if reservable.end_date > end:
				end_reservable = end
			else:
				end_reservable = reservable.end_date
			reservable_days_this_room += (end_reservable - start_reservable).days

		if room.shared:
			reservable_days_this_room *= room.beds
		reservable_days_per_room[room] = reservable_days_this_room

	total_income_for_this_month = income_for_this_month + income_from_past_months
	total_income_during_this_month = income_for_this_month + income_for_future_months + income_for_past_months
	total_by_rooms = sum(room_income.itervalues())
	for room, income in room_income.iteritems():
		# this is a bit weird, but a room can be booked by an admin even if it
		# isn't listed as reservable, effectively increasing the reservable
		# nights. we're not changing the "reservable" objects, but since it was
		# reserved, it will throw off the occupancy calculation unless we add
		# those days to the number of reservable days per room.
		# TODO *should* we add create reservables here?
		if reservable_days_per_room[room] < room_occupancy[room]:
			reservable_days_per_room[room] = room_occupancy[room]
		if reservable_days_per_room[room] > 0:
			room_occupancy_rate = 100*float(room_occupancy[room])/reservable_days_per_room[room]
		else:
			room_occupancy_rate = 0
		# tuple with income, num nights occupied, and % occupancy rate
		room_income_occupancy[room] = (income, room_occupancy[room], room_occupancy_rate)
		total_reservable_days += reservable_days_per_room[room]
	overall_occupancy = 0
	if total_reservable_days > 0:
		overall_occupancy = 100*float(total_occupied_person_nights)/total_reservable_days

	return render(request, "occupancy.html", {"data": person_nights_data, 'location': location,
		'total_occupied_person_nights':total_occupied_person_nights, 'total_income':total_income, 'unpaid_total': unpaid_total,
		'total_reservable_days': total_reservable_days, 'overall_occupancy': overall_occupancy,
		'total_shared_nights': total_shared_nights, 'total_private_nights': total_private_nights,
		'total_comped_income': total_comped_income, 'total_comped_nights': total_comped_nights,
		"next_month": next_month, "prev_month": prev_month, "report_date": report_date, 'room_income_occupancy':room_income_occupancy,
		'income_for_this_month': income_for_this_month, 'income_for_future_months':income_for_future_months,
		'income_from_past_months': income_from_past_months, 'income_for_past_months':income_for_past_months,
		'total_income_for_this_month':total_income_for_this_month, 'total_by_rooms': total_by_rooms,
		'paid_rate_discrepancy': paid_rate_discrepancy, 'payment_discrepancies': payment_discrepancies,
		'total_income_during_this_month': total_income_during_this_month, 'paid_amount_missing':paid_amount_missing,
		'average_guests_per_day': float(total_occupied_person_nights)/(end -start).days })

@login_required
def manage_today(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	today = timezone.localtime(timezone.now())

	departing_today = (Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
		.filter(location=location).filter(depart=today))

	arriving_today = (Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
		.filter(location=location).filter(arrive=today))

	events_today = published_events_today_local(location)

	return render(request, "location_manage_today.html", {'location': location, 'arriving_today': arriving_today,
		'departing_today': departing_today, 'events_today': events_today})


@login_required
def calendar(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	today = timezone.localtime(timezone.now())
	month = request.GET.get("month")
	year = request.GET.get("year")

	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	report_date = datetime.date(year, month, 1)

	reservations = (Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
		.filter(location=location).exclude(depart__lt=start).exclude(arrive__gt=end).order_by('arrive'))

	rooms = Resource.objects.filter(location=location)
	reservations_by_room = []
	empty_rooms = 0

	# this is tracked here to help us determine what height the timeline div
	# should be. it's kind of a hack.
	num_rows_in_chart = 0
	for room in rooms:
		num_rows_in_chart += room.beds

	if len(reservations) == 0:
		any_reservations = False
	else:
		any_reservations = True

	for room in rooms:
		reservations_this_room = []

		reservation_list_this_room = list(reservations.filter(resource=room))

		if len(reservation_list_this_room) == 0:
			empty_rooms += 1
			num_rows_in_chart -= room.beds

		else:
			for r in reservation_list_this_room:
				if r.arrive < start:
					display_start = start
				else:
					display_start = r.arrive
				if r.depart > end:
					display_end = end
				else:
					display_end = r.depart
				reservations_this_room.append({'reservation':r, 'display_start':display_start, 'display_end':display_end})

			reservations_by_room.append((room, reservations_this_room))

	logger.debug("Reservations by Room for calendar view:")
	logger.debug(reservations_by_room)

	# create the calendar object
	guest_calendar = GuestCalendar(reservations, year, month, location).formatmonth(year, month)

	return render(request, "calendar.html", {'reservations': reservations, 'reservations_by_room': reservations_by_room,
		'month_start': start, 'month_end': end, "next_month": next_month, "prev_month": prev_month, 'rows_in_chart': num_rows_in_chart,
		"report_date": report_date, 'location': location, 'empty_rooms': empty_rooms, 'any_reservations': any_reservations, 'calendar': mark_safe(guest_calendar) })


def room_cal_request(request, location_slug, room_id, month=None, year=None, browse_past=True):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	month = int(request.POST.get("month"))
	year = int(request.POST.get("year"))
	browse_past_str = request.POST.get("browse_past")
	if browse_past_str == 'false':
		browse_past = False
	else:
		brose_past = True

	try:
		location = get_object_or_404(Location, slug=location_slug)
		room = Resource.objects.get(id=room_id)
	except:
		return HttpResponseRedirect('/')

	cal_html = room.availability_calendar_html(month=month, year=year)
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	link_html = '''
			<form id="room-cal-prev" action="%s" class="form-inline">
				<input type="hidden" name="month" value=%s>
				<input type="hidden" name="year" value=%s>
				<input class="room-cal-req form-control" type="submit" value="Previous">
			</form>
			<form id="room-cal-next" action="%s" class="form-inline">
				<input type="hidden" name="month" value=%s>
				<input type="hidden" name="year" value=%s>
				<input class="room-cal-req form-control" type="submit" value="Next">
			</form>
	''' % (reverse(room_cal_request, args=(location.slug, room.id)), prev_month.month, prev_month.year,
			reverse(room_cal_request, args=(location.slug, room.id)), next_month.month, next_month.year)
	return HttpResponse(cal_html+link_html)

def stay(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)

	today = timezone.localtime(timezone.now())
	if browse_past == False and prev_month < datetime.date(today.year, today.month, 1):
		link_html = '''
				<div class="clear"></div>
				<div class="center">
				<span class="greyed-out">Previous</span> |
				<a id="room-cal-%s-next" href="%s?month=%s&year=%s">Next</a>
				</div>
		''' % (room_id, reverse(room_cal_request, args=(location.slug, room.id)), next_month.month, next_month.year)
	else:
		link_html = '''
				<div class="clear"></div>
				<div class="center">
				<a id="room-cal-%s-prev" href="%s?month=%s&year=%s">Previous</a> |
				<a id="room-cal-%s-next" href="%s?month=%s&year=%s">Next</a>
				</div>
		''' % (room_id, reverse(room_cal_request, args=(location.slug, room.id)), prev_month.month, prev_month.year,
				room_id, reverse(room_cal_request, args=(location.slug, room.id)), next_month.month, next_month.year)
	return HttpResponse(cal_html+link_html)

def thanks(request, location_slug):
	# TODO generate receipt
	return render(request, "thanks.html")

@login_required
def ListUsers(request):
	users = User.objects.filter(is_active=True)
	return render(request, "user_list.html", {"users": users})

@login_required
def UserDetail(request, username):
	try:
		user = User.objects.get(username=username)
	except:
		messages.add_message(request, messages.INFO, 'There is no user with that username.')
		return HttpResponseRedirect('/404')

	events = list(user.events_attending.all())
	events.reverse()
	print type(events)

	reservations = Reservation.objects.filter(user=user).exclude(status='deleted').order_by('arrive')
	subscriptions = Subscription.objects.filter(user=user).order_by('start_date')
	past_reservations = []
	upcoming_reservations = []
	for reservation in reservations:
		if reservation.arrive >= datetime.date.today():
			upcoming_reservations.append(reservation)
		else:
			past_reservations.append(reservation)
	user_is_house_admin_somewhere = False
	for location in Location.objects.filter(visibility='public'):
		if request.user in location.house_admins.all():
			user_is_house_admin_somewhere = True
			break

	# grab the rooms that this user is a backer/resident of
	room_forms = []
	rooms = user.resources.all()
	for room in rooms:
		if room.image:
			has_image = True
		else:
			has_image = False

		room_availability = SerializedRoomAvailability(room, timezone.localtime(timezone.now()))
		room_forms.append((LocationRoomForm(instance=room, prefix="room_%d" % room.id), room.id, room.name, room.location.slug, has_image, json.dumps(room_availability.as_dict())))

	return render(request, "user_details.html", {"u": user, 'user_is_house_admin_somewhere': user_is_house_admin_somewhere,
		"past_reservations": past_reservations, "upcoming_reservations": upcoming_reservations, 'subscriptions': subscriptions,
		"room_forms": room_forms, "events": events, "stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY})

def location_list(request):
	locations = Location.objects.filter(visibility='public').order_by("name")
	return render(request, "location_list.html", {"locations": locations})

def date_range_to_list(start, end):
	the_day = start
	date_list = []
	while the_day < end:
		date_list.append(the_day)
		the_day = the_day + datetime.timedelta(1)
	return date_list

def CheckRoomAvailability(request, location_slug):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	location = get_object_or_404(Location, slug=location_slug)
	arrive_str = request.POST.get('arrive')
	depart_str = request.POST.get('depart')
	a_month, a_day, a_year = arrive_str.split("/")
	d_month, d_day, d_year = depart_str.split("/")
	arrive = datetime.date(int(a_year), int(a_month), int(a_day))
	depart = datetime.date(int(d_year), int(d_month), int(d_day))
	availability = location.availability(arrive, depart)
	date_list = date_range_to_list(arrive, depart)
	logger.debug("Checking room availability for date list")
	logger.debug(date_list)
	available_reservations = {}
	# Create some mock reservations for each available room so we can generate the bill
	free_rooms = location.rooms_free(arrive, depart)
	for room in free_rooms:
		reservation = Reservation(id=-1, resource=room, arrive=arrive, depart=depart, location=location)
		bill_line_items = reservation.generate_bill(delete_old_items=False, save=False)
		total = Decimal(0.0)
		for item in bill_line_items:
			if not item.paid_by_house:
				total = Decimal(total) + Decimal(item.amount)
		nights = reservation.total_nights()
		available_reservations[room] = {'reservation':reservation, 'bill_line_items':bill_line_items, 'nights':nights, 'total':total}

	new_profile_form = UserProfileForm()
	if request.user.is_authenticated():
		current_user = request.user
	else:
		current_user = None

	# base previous and next on the arrival date. note that these dates will
	# also have a day associated with them but we don't use that.
	prev_month = arrive - relativedelta(months=1)
	next_month = arrive + relativedelta(months=1)

	all_users = User.objects.all().order_by('username')
	return render(request, "snippets/availability_calendar.html", {"availability_table": availability, "dates": date_list, "current_user": current_user,
		'available_reservations': available_reservations, 'arrive_date': arrive_str, 'depart_date': depart_str, 'arrive': arrive, 'depart': depart,
		"new_profile_form": new_profile_form, 'all_users': all_users, 'prev_month':prev_month, 'next_month': next_month})

@csrf_exempt
def RoomsAvailableOnDates(request, location_slug):
	'''
		Args:
			request (http request obj): Request object sent from ajax request, includes arrive, depart and room data
			location_slug (string): name of location

		Returns:
			Boolean: True if room is available. False if not available.

	'''
	# Check the room on the admin reservation page to see if its available
	location = get_object_or_404(Location, slug=location_slug)
	# Check if the room is available for all dates in the reservation
	try:
		arrive = datetime.datetime.strptime(request.POST['arrive'],'%m/%d/%Y').date()
		depart = datetime.datetime.strptime(request.POST['depart'],'%m/%d/%Y').date()
	except:
		arrive = datetime.datetime.strptime(request.POST['arrive'],'%Y-%m-%d').date()
		depart = datetime.datetime.strptime(request.POST['depart'],'%Y-%m-%d').date()
	free_rooms = location.rooms_free(arrive, depart)
	rooms_availability = {}
	for room in location.rooms_with_future_reservability():
		if room in free_rooms:
			rooms_availability[room.name] = {'available': True, 'id': room.id}
		else:
			rooms_availability[room.name] = {'available': False, 'id': room.id}
	return JsonResponse({'rooms_availability': rooms_availability})

def ReservationSubmit(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	if request.method == 'POST':
		form = ReservationForm(location, request.POST)
		if form.is_valid():
			reservation = form.save(commit=False)
			reservation.location = location
			if request.user.is_authenticated():
				reservation.user = request.user
				reservation.save()
				# Make sure the rate is set and then generate a bill
				reservation.reset_rate()
				new_reservation_notify(reservation)
				messages.add_message(request, messages.INFO, 'Thanks! Your reservation was submitted. You will receive an email when it has been reviewed. You may wish to <a href="/people/%s/edit/">update your profile</a> if your projects or ideas have changed since your last visit.' % reservation.user.username)
				return HttpResponseRedirect(reverse('reservation_detail', args=(location_slug, reservation.id)))
			else:
				res_info = reservation.serialize()
				request.session['reservation'] = res_info
				messages.add_message(request, messages.INFO, 'Thank you! Please make a profile to complete your reservation request.')
				return HttpResponseRedirect(reverse('registration_register'))
		else:
			logger.debug(request.POST)
			logger.debug(form.errors)
	# GET request
	else:
		form = ReservationForm(location)
	# pass the rate for each room to the template so we can update the cost of
	# a reservation in real time.
	today = timezone.localtime(timezone.now())
	month = request.GET.get("month")
	year = request.GET.get("year")
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	rooms = location.rooms_with_future_reservability()
	return render(request, 'reservation.html', {'form': form, 'max_days': location.max_reservation_days, 'location': location, 'rooms': rooms,
		'prev_month': prev_month, 'next_month': next_month, 'month': month })


@login_required
def ReservationDetail(request, reservation_id, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	try:
		reservation = Reservation.objects.get(id=reservation_id)
		if not reservation:
			raise Reservation.DoesNotExist
	except Reservation.DoesNotExist:
		msg = 'The reservation you requested do not exist'
		messages.add_message(request, messages.ERROR, msg)
		return HttpResponseRedirect('/404')
	# make sure the user is either an admin, resident or the reservation holder
	# (we can't use the decorator here because the user themselves also has to
	# be able to see the page).
	if ((request.user == reservation.user) or
			(request.user in location.house_admins.all()) or
			(request.user in location.readonly_admins.all()) or
			(request.user in location.residents.all())):
		if reservation.arrive >= datetime.date.today():
			past = False
		else:
			past = True
		if reservation.is_paid():
			paid = True
		else:
			paid = False

		domain = Site.objects.get_current().domain

		# users that intersect this stay
		users_during_stay = []
		reservations = Reservation.objects.filter(status="confirmed").filter(location=location).exclude(depart__lt=reservation.arrive).exclude( arrive__gt=reservation.depart)
		for res in reservations:
			if res.user not in users_during_stay:
				users_during_stay.append(res.user)
		for member in location.residents.all():
			if member not in users_during_stay:
				users_during_stay.append(member)

		# events that intersected your stay
		#events_during_stay = []
		#all_events = Event.objects.filter(location=location).exclude(end__lt=reservation.arrive).exclude( start__gt=reservation.depart)
		#events_during_stay += list(all_events.filter(status="public"))
		# if they are a member, include the community-only events
		#if request.user in location.residents.all():
		#	events_during_stay += list(all_events.filter(status="community"))
		# if they RSVPed for any private events, include those
		#private = all_events.filter(status="private").filter(attendees__in=[request.user,])
		#if len(private) > 0:
		#	events_during_stay += list(private)

		return render(request, "reservation_detail.html", {"reservation": reservation, "past":past, 'location': location, "domain": domain,
			"stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY, "paid": paid, "contact" : location.from_email(),
			'users_during_stay': users_during_stay })
	else:
		messages.add_message(request, messages.INFO, "You do not have permission to view that reservation")
		return HttpResponseRedirect('/404')

@csrf_exempt
def username_available(request):
	'''AJAX request to check for existing user with the submitted username'''
	logger.debug('in username_available')
	if not request.is_ajax():
		return HttpResponseRedirect('/404')
	username = request.POST.get('username')
	users_with_username = len(User.objects.filter(username=username))
	if users_with_username:
		logger.debug('username %s is already in use' % username)
		is_available = 'false'
	else:
		logger.debug('username %s is available' % username)
		is_available = 'true'
	return HttpResponse(is_available)

@csrf_exempt
def email_available(request):
	'''AJAX request to check for existing user with the submitted email'''
	logger.debug('in email_available')
	if not request.is_ajax():
		return HttpResponseRedirect('/404')
	email = request.POST.get('email').lower()
	users_with_email = len(User.objects.filter(email=email))
	if users_with_email:
		logger.debug('email address %s is already in use' % email)
		is_available = 'false'
	else:
		logger.debug('email address %s is available' % email)
		is_available = 'true'
	return HttpResponse(is_available)

@login_required
def UserAvatar(request, username):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	user = get_object_or_404(User, username=username)
	try:
		url = user.profile.image.url
	except:
		url = '/static/img/default.jpg'
	return HttpResponse(url)


@login_required
def UserAddCard(request, username):
	''' Adds a card from either the reservation page or the user profile page.
	Displays success or error message and returns user to originating page.'''

	print "in user add card"
	# get the user object associated with the reservation
	user = get_object_or_404(User, username=username)
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	reservation_id = request.POST.get('res-id', False)
	if reservation_id:
		reservation = Reservation.objects.get(id=reservation_id)
		# double checks that the authenticated user (the one trying to add the
		# card) is the user associated with this reservation, or an admin (i am
		# not sure this is necessary since you need to be the reservation user
		# or a house admin to view the reservation in the first place!).
		if (request.user != user) and (request.user not in reservation.location.house_admins.all() ):
			print 'there was an error adding the user\'s card: authenticated user is not the reservation user'
			print request.POST
			print request.user
			messages.add_message(request, messages.INFO, "You are not authorized to add a credit card to this page. Please log in or use the 3rd party")
			return HttpResponseRedirect('/404')

	token = request.POST.get('stripeToken')
	if not token:
		messages.add_message(request, messages.INFO, "No credit card information was given.")
		if reservation_id:
			return HttpResponseRedirect(reverse('reservation_detail', args=(reservation.location.slug, reservation.id)))
		return HttpResponseRedirect("/people/%s" % username)

	stripe.api_key = settings.STRIPE_SECRET_KEY

	try:
		customer = stripe.Customer.create(card=token, description=user.email)
		print 'customer'
		print customer
		profile = user.profile
		profile.customer_id = customer.id
		print customer.sources.data
		# assumes the user has only one card stored with their profile.
		profile.last4 = customer.sources.data[0].last4
		profile.save()
		if reservation_id and reservation.status == Reservation.APPROVED:
			updated_reservation_notify(reservation)
		messages.add_message(request, messages.INFO, 'Thanks! Your card has been saved.')
	except Exception, e:
		messages.add_message(request, messages.INFO, '<span class="text-danger">Drat, there was a problem with your card: <em>%s</em></span>' % e)
	if reservation_id:
		return HttpResponseRedirect(reverse('reservation_detail', args=(reservation.location.slug, reservation.id)))
	return HttpResponseRedirect("/people/%s" % username)



def UserDeleteCard(request, username):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	profile = UserProfile.objects.get(user__username=username)
	profile.customer_id = None
	profile.last4 = None
	profile.save()

	messages.add_message(request, messages.INFO, "Card deleted.")
	return HttpResponseRedirect("/people/%s" % profile.user.username)

@login_required
def ReservationEdit(request, reservation_id, location_slug):
	logger.debug("Entering ReservationEdit")

	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	# need to pull these dates out before we pass the instance into
	# the ReservationForm, since it (apparently) updates the instance
	# immediately (which is weird, since it hasn't validated the form
	# yet!)
	original_arrive = reservation.arrive
	original_depart = reservation.depart
	original_room = reservation.resource
	if request.user.is_authenticated() and request.user == reservation.user:
		logger.debug("ReservationEdit: Authenticated and same user")
		if request.user in reservation.location.house_admins.all():
			is_house_admin = True
		else:
			is_house_admin = False

		if request.method == "POST":
			logger.debug("ReservationEdit: POST")
			# don't forget to specify the "instance" argument or a new object will get created!
			#form = get_reservation_form_for_perms(request, post=True, instance=reservation)
			form = ReservationForm(location, request.POST, instance=reservation)
			if form.is_valid():
				logger.debug("ReservationEdit: Valid Form")

				# if the dates have been changed, and the reservation isn't
				# still pending to begin with, notify an admin and go back to
				# pending.
				logger.debug("is_pending: %s" % reservation.is_pending())
				logger.debug("arrive: %s, original: %s" % (reservation.arrive, original_arrive))
				logger.debug("depart: %s, original: %s" % (reservation.depart, original_depart))
				logger.debug("room: %s, original: %s" % (reservation.resource, original_room))
				if (not reservation.is_pending() and (reservation.arrive != original_arrive or
					reservation.depart != original_depart or reservation.room != original_room )):
					logger.debug("reservation room or date was changed. updating status.")
					reservation.pending()
					# notify house_admins by email
					try:
						updated_reservation_notify(reservation)
					except:
						logger.debug("Reservation %d was updated but admin notification failed to send" % reservation.id)
					client_msg = 'The reservation was updated and the new information will be reviewed for availability.'
				else:
					client_msg = 'The reservation was updated.'
				# save the instance *after* the status has been updated as needed.
				form.save()
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect(reverse("reservation_detail", args=(location.slug, reservation_id)))
		else:
			#form = get_reservation_form_for_perms(request, post=False, instance=reservation)
			form = ReservationForm(location, instance=reservation)

		return render(request, 'reservation_edit.html', {'form': form, 'reservation_id': reservation_id,
			'arrive': reservation.arrive, 'depart': reservation.depart, 'is_house_admin' : is_house_admin,
			'max_days': location.max_reservation_days, 'location': location })

	else:
		return HttpResponseRedirect("/")

@login_required
def ReservationConfirm(request, reservation_id, location_slug):
	reservation = Reservation.objects.get(id=reservation_id)
	if not (request.user.is_authenticated() and request.user == reservation.user
		and request.method == "POST" and reservation.is_approved()):
		return HttpResponseRedirect("/")

	if not reservation.user.profile.customer_id:
		messages.add_message(request, messages.INFO, 'Please enter payment information to confirm your reservation.')
	else:
		try:
			payment_gateway.charge_reservation(reservation)
			reservation.confirm()
			send_reservation_receipt(reservation)
			# if reservation start date is sooner than WELCOME_EMAIL_DAYS_AHEAD,
			# need to send them house info manually.
			days_until_arrival = (reservation.arrive - datetime.date.today()).days
			if days_until_arrival <= reservation.location.welcome_email_days_ahead:
				guest_welcome(reservation)
			messages.add_message(request, messages.INFO, 'Thank you! Your payment has been received and a receipt emailed to you at %s' % reservation.user.email)
		except stripe.CardError, e:
			messages.add_message(request, messages.WARNING, 'Drat, it looks like there was a problem with your card: %s. Please add a different card on your <a href="/people/%s/edit/">profile</a>.' % (reservation.user.username, e))

	return HttpResponseRedirect(reverse('reservation_detail', args=(location_slug, reservation.id)))

@login_required
def ReservationCancel(request, reservation_id, location_slug):
	if not request.method == "POST":
		return HttpResponseRedirect("/404")

	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	if (not (request.user.is_authenticated() and request.user == reservation.user)
			and not request.user in location.house_admins.all()):
		return HttpResponseRedirect("/404")

	redirect = request.POST.get("redirect")

	reservation.cancel()
	messages.add_message(request, messages.INFO, 'The reservation has been cancelled.')
	username = reservation.user.username
	return HttpResponseRedirect(redirect)


@login_required
def ReservationDelete(request, reservation_id, location_slug):
	reservation = Reservation.objects.get(id=reservation_id)
	if (request.user.is_authenticated() and request.user == reservation.user
		and request.method == "POST"):
		reservation.cancel()

		messages.add_message(request, messages.INFO, 'Your reservation has been cancelled.')
		username = reservation.user.username
		return HttpResponseRedirect("/people/%s" % username)

	else:
		return HttpResponseRedirect("/")

	html += "</div>"
	return HttpResponse(html)


@house_admin_required
def LocationEditSettings(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	if request.method == 'POST':
		form = LocationSettingsForm(request.POST, instance=location)
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.INFO, "Location Updated.")
	else:
		form = LocationSettingsForm(instance=location)
	return render(request, 'location_edit_settings.html', {'page':'settings', 'location': location, 'form':form})

@house_admin_required
def LocationEditUsers(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	if request.method == 'POST':
		admin_user = resident_user = event_admin_user = readonly_admin_user = None
		if 'admin_username' in request.POST:
			admin_username = request.POST.get('admin_username')
			admin_user = User.objects.filter(username=admin_username).first()
		elif 'resident_username' in request.POST:
			resident_username = request.POST.get('resident_username')
			resident_user = User.objects.filter(username=resident_username).first()
		elif 'readonly_admin_username' in request.POST:
			readonly_admin_username = request.POST.get('readonly_admin_username')
			readonly_admin_user = User.objects.filter(username=readonly_admin_username).first()
		elif 'event_admin_username' in request.POST:
			event_admin_username = request.POST.get('event_admin_username')
			event_admin_user = User.objects.filter(username=event_admin_username).first()

		if admin_user:
			action = request.POST.get('action')
			if action == "Remove":
				# Remove user
				location.house_admins.remove(admin_user)
				location.save()
				messages.add_message(request, messages.INFO, "User '%s' removed from house admin group." % admin_username)
			elif action == "Add":
				# Add user
				location.house_admins.add(admin_user)
				location.save()
				messages.add_message(request, messages.INFO, "User '%s' added to house admin group." % admin_username)
		elif resident_user:
			action = request.POST.get('action')
			if action == "Remove":
				# Remove user
				location.residents.remove(resident_user)
				location.save()
				messages.add_message(request, messages.INFO, "User '%s' removed from residents group." % resident_username)
			elif action == "Add":
				# Add user
				location.residents.add(resident_user)
				location.save()
				messages.add_message(request, messages.INFO, "User '%s' added to residents group." % resident_username)
		elif readonly_admin_user:
			action = request.POST.get('action')
			if action == "Remove":
				# Remove user
				location.readonly_admins.remove(readonly_admin_user)
				location.save()
				messages.add_message(request, messages.INFO, "User '%s' removed from readonly admin group." % readonly_admin_username)
			elif action == "Add":
				# Add user
				location.readonly_admins.add(readonly_admin_user)
				location.save()
				messages.add_message(request, messages.INFO, "User '%s' added to readonly admin group." % readonly_admin_username)
		elif event_admin_user:
			action = request.POST.get('action')
			if action == "Remove":
				# Remove user
				event_admin_group = location.event_admin_group
				event_admin_group.users.remove(event_admin_user)
				event_admin_group.save()
				messages.add_message(request, messages.INFO, "User '%s' removed from event admin group." % event_admin_username)
			elif action == "Add":
				# Add user
				event_admin_group = location.event_admin_group
				event_admin_group.users.add(event_admin_user)
				event_admin_group.save()
				messages.add_message(request, messages.INFO, "User '%s' added to event admin group." % event_admin_username)
		else:
			messages.add_message(request, messages.ERROR, "Username Required!")
	all_users = User.objects.all().order_by('username')
	return render(request, 'location_edit_users.html', {'page':'users', 'location': location, 'all_users':all_users})

@house_admin_required
def LocationEditPages(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)

	if request.method == 'POST':
		action = request.POST['action']
		print "action=%s" % action
		print request.POST
		if "Add Menu" == action:
			try:
				menu = request.POST['menu'].strip().title()
				if menu and not LocationMenu.objects.filter(location=location, name=menu).count() > 0:
					LocationMenu.objects.create(location=location, name=menu)
			except Exception as e:
				messages.add_message(request, messages.ERROR, "Could not create menu: %s" % e)
		elif "Delete Menu" == action and 'menu_id' in request.POST:
			try:
				menu = LocationMenu.objects.get(pk=request.POST['menu_id'])
				menu.delete()
			except Exception as e:
				messages.add_message(request, messages.ERROR, "Could not delete menu: %s" % e)
		elif "Save Changes" == action and 'page_id' in request.POST:
			try:
				page = LocationFlatPage.objects.get(pk=request.POST['page_id'])
				menu = LocationMenu.objects.get(pk=request.POST['menu'])
				page.menu = menu
				page.save()

				url_slug = request.POST['slug'].strip().lower()
				page.flatpage.url = "/locations/%s/%s/" % (location.slug, url_slug)
				page.flatpage.title = request.POST['title']
				page.flatpage.content = request.POST['content']
				page.flatpage.save()
				messages.add_message(request, messages.INFO, "The page was updated.")
			except Exception as e:
				messages.add_message(request, messages.ERROR, "Could not edit page: %s" % e)
		elif "Delete Page" == action and 'page_id' in request.POST:
			print "in Delete Page"
			try:
				page = LocationFlatPage.objects.get(pk=request.POST['page_id'])
				page.delete()
				messages.add_message(request, messages.INFO, "The page was deleted")
			except Exception as e:
				messages.add_message(request, messages.ERROR, "Could not delete page: %s" % e)
		elif "Create Page" == action:
			try:
				menu = LocationMenu.objects.get(pk=request.POST['menu'])
				url_slug = request.POST['slug'].strip().lower()
				url = "/locations/%s/%s/" % (location.slug, url_slug)
				if not url_slug or FlatPage.objects.filter(url=url).count() != 0:
					raise Exception("Invalid slug (%s)" % url_slug)
				flatpage = FlatPage.objects.create(url=url, title=request.POST['title'], content=request.POST['content'])
				flatpage.sites.add(Site.objects.get_current())
				LocationFlatPage.objects.create(menu=menu, flatpage=flatpage)
			except Exception as e:
				messages.add_message(request, messages.ERROR, "Could not edit page: %s" % e)

	menus = location.get_menus()
	new_page_form = LocationPageForm(location=location)

	page_forms = {}
	for page in LocationFlatPage.objects.filter(menu__location=location):
		form = LocationPageForm(location=location, initial={'menu':page.menu, 'slug':page.slug, 'title':page.title, 'content':page.content})
		page_forms[page] = form

	return render(request, 'location_edit_pages.html', {'page':'pages', 'location': location, 'menus':menus,
		'page_forms':page_forms, 'new_page_form':new_page_form})

@resident_or_admin_required
def LocationEditRooms(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)

	location_rooms = location.resources.all().order_by('name')

	if request.method == 'POST':
		print 'received new room or room data'
		if request.POST.get("room_id"):
			room_id = int(request.POST.get("room_id"))
			if room_id > 0:
				# editing an existing item
				print 'updating an existing room'
				action = "updated"
				room = Resource.objects.get(id=room_id)
				# request.POST keys now have a prefix, so don't forget to pass that along here!
				prefix = "room_%d" % room_id
				form = LocationRoomForm(request.POST, request.FILES, instance=room, prefix=prefix)
			else:
				# new item
				action = "created"
				form = LocationRoomForm(request.POST, request.FILES)
			if form.is_valid():
				if action == "updated":
					form.save()
					messages.add_message(request, messages.INFO, "%s %s." % (room.name, action))
				else:
					new_room = form.save(commit=False)
					new_room.location = location
					new_room.save()
					messages.add_message(request, messages.INFO, "%s %s." % (new_room.name, action))
			else:
				messages.add_message(request, messages.INFO, "Form error(s): %s." % form.errors)
		elif request.POST.get("reservable_id"):
			reservable_id = int(request.POST.get("reservable_id"))
			if reservable_id > 0:
				# editing an existing reservable
				action = "updated"
				reservable = Reservable.objects.get(id=reservable_id)
				form = LocationReservableForm(request.POST, request.FILES, instance=reservable)
			else:
				# creating a new reservable
				action = "created"
				form = LocationReservableForm(request.POST, request.FILES)

			if form.is_valid():
				if action == "updated":
					form.save()
				else:
					room_fk = request.POST.get('room_fk')
					room = Resource.objects.get(id=room_fk)
					new_reservable = form.save(commit=False)
					new_reservable.resource = room
					new_reservable.save()
				room = Resource.objects.get(id=request.POST.get('room_fk'))
				messages.add_message(request, messages.INFO, "Reservable date range %s for %s." % (action, room.name))
			else:
				messages.add_message(request, messages.INFO, "Form error(s): %s." % form.errors)
		else:
			messages.add_message(request, messages.INFO, "Error: no id was provided.")

	page = request.POST.get('page')
	if page == 'user_detail':
		print 'redirecting to user page'
		return HttpResponseRedirect(reverse('user_detail', args=(request.POST.get('username'), )))
	else:
		room_forms = []
		room_names = []
		room_names.append("New Room")
		# the empty form
		room_availability = SerializedNullRoomAvailability()
		room_forms.append((LocationRoomForm(prefix="new"), -1, "new room", location.slug, False, json.dumps(room_availability.as_dict())))

		# forms for the existing rooms
		for room in location_rooms:
			if room.image:
				has_image = True
			else:
				has_image = False

			room_availability = SerializedRoomAvailability(room, timezone.localtime(timezone.now()))

			room_forms.append((LocationRoomForm(instance=room, prefix="room_%d" % room.id),
				room.id, room.name, room.location.slug, has_image, json.dumps(room_availability.as_dict())))
			room_names.append(room.name)

		return render(request, 'location_edit_rooms.html', {'page':'rooms', 'location': location, 'room_forms':room_forms, 'room_names': room_names, 'location_rooms': location_rooms,})

@house_admin_required
def LocationEditContent(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	if request.method == 'POST':
		form = LocationContentForm(request.POST, request.FILES, instance=location)
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.INFO, "Location Updated.")
	else:
		form = LocationContentForm(instance=location)
	return render(request, 'location_edit_content.html', {'page':'content', 'location': location, 'form':form})

@house_admin_required
def LocationEditEmails(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	form = LocationSettingsForm(instance=location)
	return render(request, 'location_edit_settings.html', {'page':'emails', 'location': location, 'form':form})

# ******************************************************
#           reservation management views
# ******************************************************

@house_admin_required
def ReservationManageList(request, location_slug):
	if request.method == "POST":
		reservation_id = request.POST.get('reservation_id')
		reservation = get_object_or_404(Reservation, id=reservation_id)
		return HttpResponseRedirect(reverse('reservation_manage', args=(reservation.location.slug, reservation.id)))

	location = get_object_or_404(Location, slug=location_slug)

	show_all = False
	if 'show_all' in request.GET and request.GET.get('show_all') == "True":
		show_all = True

	pending = Reservation.objects.filter(location=location).filter(status="pending").order_by('-id')
	approved = Reservation.objects.filter(location=location).filter(status="approved").order_by('-id')
	confirmed = Reservation.objects.filter(location=location).filter(status="confirmed").order_by('-id')
	canceled = Reservation.objects.filter(location=location).exclude(status="confirmed").exclude(status="approved").exclude(status="pending").order_by('-id')
	if not show_all:
		today = timezone.localtime(timezone.now())
		confirmed = confirmed.filter(depart__gt=today)
		canceled =  canceled.filter(depart__gt=today)
	owing = Reservation.objects.confirmed_but_unpaid(location=location)
	return render(request, 'reservation_list.html', {"pending": pending, "approved": approved,
		"confirmed": confirmed, "canceled": canceled, "owing": owing, 'location': location})

@house_admin_required
def ReservationManageCreate(request, location_slug):
	username=""
	if request.method == 'POST':
		location = get_object_or_404(Location, slug=location_slug)

		notify = request.POST.get('email_announce');
		print 'notify was set to:'
		print notify

		try:
			username = request.POST.get('username');
			the_user = User.objects.get(username=username)
		except:
			messages.add_message(request, messages.INFO, "There is no user with the username %s" % username)
			return HttpResponseRedirect(reverse('reservation_manage_create', args=(location.slug,)))

		form = AdminReservationForm(request.POST)
		if form.is_valid():
			reservation = form.save(commit=False)
			reservation.location = location
			reservation.user = the_user
			reservation.status = request.POST.get('status')
			reservation.save()
			# Make sure the rate is set and then generate a bill
			reservation.reset_rate()
			if notify:
				new_reservation_notify(reservation)
			messages.add_message(request, messages.INFO, "The reservation for %s %s was created." % (reservation.user.first_name, reservation.user.last_name))
			return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation.id)))
		else:
			print 'the form had errors'
			print form.errors
	else:
		form = AdminReservationForm()
		username = request.GET.get("username", "")
	all_users = User.objects.all().order_by('username')
	return render(request, 'reservation_manage_create.html', {'all_users': all_users, "reservation_statuses": Reservation.RESERVATION_STATUSES, "username": username })


@house_admin_required
def ReservationManage(request, location_slug, reservation_id):
	location = get_object_or_404(Location, slug=location_slug)
	reservation = get_object_or_404(Reservation, id=reservation_id)
	user = User.objects.get(username=reservation.user.username)
	other_reservations = Reservation.objects.filter(user=user).exclude(status='deleted').exclude(id=reservation_id)
	past_reservations = []
	upcoming_reservations = []
	for res in other_reservations:
		if res.arrive >= datetime.date.today():
			upcoming_reservations.append(res)
		else:
			past_reservations.append(res)
	domain = Site.objects.get_current().domain
	emails = EmailTemplate.objects.filter(context='reservation').filter(Q(shared=True) | Q(creator=request.user))
	email_forms = []
	email_templates_by_name = []
	for email_template in emails:
		form = ReservationEmailTemplateForm(email_template, reservation, location)
		email_forms.append(form)
		email_templates_by_name.append(email_template.name)

	availability = location.availability(reservation.arrive, reservation.depart)
	free = location.rooms_free(reservation.arrive, reservation.depart)
	date_list = date_range_to_list(reservation.arrive, reservation.depart)
	if reservation.resource in free:
		room_has_availability = True
	else:
		room_has_availability = False

	# Pull all the reservation notes for this person
	if 'note' in request.POST:
		note = request.POST['note']
		if note:
			ReservationNote.objects.create(reservation=reservation, created_by=request.user, note=note)
			# The Right Thing is to do an HttpResponseRedirect after a form
			# submission, which clears the POST request data (even though we
			# are redirecting to the same view)
			return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, reservation_id)))
	reservation_notes = ReservationNote.objects.filter(reservation=reservation)

	# Pull all the user notes for this person
	if 'user_note' in request.POST:
		note = request.POST['user_note']
		if note:
			UserNote.objects.create(user=user, created_by=request.user, note=note)
			# The Right Thing is to do an HttpResponseRedirect after a form submission
			return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, reservation_id)))
	user_notes = UserNote.objects.filter(user=user)

	return render(request, 'reservation_manage.html', {
		"r": reservation,
		"past_reservations":past_reservations,
		"upcoming_reservations": upcoming_reservations,
		"user_notes": user_notes,
		"reservation_notes": reservation_notes,
		"email_forms" : email_forms,
		"reservation_statuses": Reservation.RESERVATION_STATUSES,
		"email_templates_by_name" : email_templates_by_name,
		"days_before_welcome_email" : location.welcome_email_days_ahead,
		"room_has_availability" : room_has_availability,
		"avail": availability, "dates": date_list,
		"domain": domain, 'location': location,
	})

@house_admin_required
def ReservationManageAction(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	reservation_action = request.POST.get('reservation-action')

	if reservation_action == 'set-tentative':
		reservation.approve()
	elif reservation_action == 'set-confirm':
		reservation.confirm()
		days_until_arrival = (reservation.arrive - datetime.date.today()).days
		if days_until_arrival <= location.welcome_email_days_ahead:
			guest_welcome(reservation)
	elif reservation_action == 'set-comp':
		reservation.comp()
	elif reservation_action == 'res-charge-card':
		try:
			payment_gateway.charge_reservation(reservation)
			reservation.confirm()
			send_reservation_receipt(reservation)
			days_until_arrival = (reservation.arrive - datetime.date.today()).days
			if days_until_arrival <= location.welcome_email_days_ahead:
				guest_welcome(reservation)
		except stripe.CardError, e:
			#raise Reservation.ResActionError(e)
			#messages.add_message(request, messages.INFO, "There was an error: %s" % e)
			#status_area_html = render(request, "snippets/res_status_area.html", {"r": reservation, 'location': location, 'error': True})
			return HttpResponse(status=500)
	else:
		raise Reservation.ResActionError("Unrecognized action.")

	messages.add_message(request, messages.INFO, 'Your action has been registered!')
	status_area_html = render(request, "snippets/res_status_area.html", {"r": reservation, 'location': location, 'error': False})
	return status_area_html


@house_admin_required
def ReservationManageEdit(request, location_slug, reservation_id):
	logger.debug("ReservationManageEdit")
	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	logger.debug(request.POST)
	if 'username' in request.POST:
		try:
			new_user = User.objects.get(username=request.POST.get("username"))
			reservation.user = new_user
			reservation.save()
			messages.add_message(request, messages.INFO, "User changed.")
		except:
			messages.add_message(request, messages.INFO, "Invalid user given!")
	elif 'arrive' in request.POST:
		try:
			arrive = datetime.datetime.strptime(request.POST.get("arrive"), "%Y-%m-%d")
			depart = datetime.datetime.strptime(request.POST.get("depart"), "%Y-%m-%d")
			if arrive >= depart:
				messages.add_message(request, messages.INFO, "Arrival must be at least 1 day before Departure.")
			else:
				reservation.arrive = arrive
				reservation.depart = depart
				reservation.save()
				reservation.generate_bill()
				messages.add_message(request, messages.INFO, "Dates changed.")
		except:
			messages.add_message(request, messages.INFO, "Invalid dates given!")

	elif 'status' in request.POST:
		try:
			status = request.POST.get("status")
			reservation.status = status
			reservation.save()
			if status == "confirmed":
				messages.add_message(request, messages.INFO, "Status changed. You must manually send a confirmation email if desired.")
			else:
				messages.add_message(request, messages.INFO, "Status changed.")
		except:
			messages.add_message(request, messages.INFO, "Invalid room given!")
	elif 'room_id' in request.POST:
		try:
			new_room = Resource.objects.get(pk=request.POST.get("room_id"))
			reservation.resource = new_room
			reservation.save()
			reservation.reset_rate()
			messages.add_message(request, messages.INFO, "Room changed.")
		except:
			messages.add_message(request, messages.INFO, "Invalid room given!")
	elif 'rate' in request.POST:
		rate = request.POST.get("rate")
		if rate >= 0 and rate != reservation.get_rate():
			reservation.set_rate(rate)
			messages.add_message(request, messages.INFO, "Rate changed.")
		else:
			messages.add_message(request, messages.ERROR, "Room rate must be a positive number")

	return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, reservation_id)))

@house_admin_required
def ManagePayment(request, location_slug, bill_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	bill = get_object_or_404(Bill, id=bill_id)

	logger.debug(request.POST)
	action = request.POST.get("action")
	if action == "Submit":
		# process a refund
		payment_id = request.POST.get("payment_id")
		payment = get_object_or_404(Payment, id=payment_id)
		refund_amount = request.POST.get("refund-amount")
		print refund_amount
		print payment.net_paid()
		if Decimal(refund_amount) > Decimal(payment.net_paid()):
			messages.add_message(request, messages.INFO, "Cannot refund more than payment balance")
		else:
			payment_gateway.issue_refund(payment, refund_amount)
			if bill.is_reservation_bill():
				messages.add_message(request, messages.INFO, "A refund for $%d was applied." % (Decimal(refund_amount)))
			else:
				messages.add_message(request, messages.INFO, "A refund for $%d was applied to the %s billing cycle." % (Decimal(refund_amount), bill.subscriptionbill.period_start.strftime("%B %d, %Y")))
	elif action == "Save":
		logger.debug("saving record of external payment")
		# record a manual payment
		payment_method = request.POST.get("payment_method").strip().title()
		paid_amount = request.POST.get("paid_amount").strip()
		# JKS we store user = None for cash payments since we don't know for
		# certain *who* it was that made the payment. in the future, we could
		# allow admins to enter who made the payment, if desired.
		pmt = Payment.objects.create(payment_method = payment_method,
			paid_amount = paid_amount, bill = bill, user = None,
			transaction_id = "Manual"
		)
		if bill.is_reservation_bill():
			messages.add_message(request, messages.INFO, "Manual payment recorded")
		else:
			messages.add_message(request, messages.INFO, "A manual payment for $%d was applied to the %s billing cycle" % (Decimal(paid_amount), bill.subscriptionbill.period_start.strftime("%B %d, %Y")))

	# JKS this is a little inelegant as it assumes that this page will always
	# a) want to redirect to a manage page and b) that there are only two types
	# of bills. this should be abstracted at some point.
	if bill.is_reservation_bill():
		return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, bill.reservationbill.reservation.id)))
	else:
		return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, bill.subscriptionbill.subscription.id)))

@house_admin_required
def ReservationSendWelcomeEmail(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	if reservation.is_confirmed():
		guest_welcome(reservation)
		messages.add_message(request, messages.INFO, "The welcome email was sent.")
	else:
		messages.add_message(request, messages.INFO, "The reservation is not comfirmed, so the welcome email was not sent.")
	return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))

@house_admin_required
def SubscriptionSendReceipt(request, location_slug, subscription_id, bill_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	subscription = Subscription.objects.get(id=subscription_id)
	bill = Bill.objects.get(id=bill_id)
	if bill.is_paid():
		status = send_subscription_receipt(subscription, bill)
		if status != False:
			messages.add_message(request, messages.INFO, "A receipt was sent.")
		else:
			messages.add_message(request, messages.INFO, "Hmm, there was a problem and the receipt was not sent. Please contact an administrator.")
	else:
		messages.add_message(request, messages.INFO, "This reservation has not been paid, so the receipt was not sent.")
	return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription_id)))

@house_admin_required
def ReservationSendReceipt(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	if reservation.is_paid():
		status = send_reservation_receipt(reservation)
		if status != False:
			messages.add_message(request, messages.INFO, "The receipt was sent.")
		else:
			messages.add_message(request, messages.INFO, "Hmm, there was a problem and the receipt was not sent. Please contact an administrator.")
	else:
		messages.add_message(request, messages.INFO, "This reservation has not been paid, so the receipt was not sent.")
	return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))

@house_admin_required
def RecalculateBill(request, location_slug, bill_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	bill = get_object_or_404(Bill, id=bill_id)

	# what kind of bill is this?
	if bill.is_reservation_bill():
		reservation = bill.reservationbill.reservation
		reset_suppressed = request.POST.get('reset_suppressed')
		if reset_suppressed == "true":
			reservation.generate_bill(reset_suppressed=True)
		else:
			reservation.generate_bill()
		messages.add_message(request, messages.INFO, "The bill has been recalculated.")
		return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation.id)))
	elif bill.is_subscription_bill():
		subscription = bill.subscriptionbill.subscription
		subscription.generate_bill()
		messages.add_message(request, messages.INFO, "The bill has been recalculated.")
		return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location.slug, subscription.id)))
	else:
		raise Exception('Unrecognized bill object')

@house_admin_required
def ReservationToggleComp(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	reservation = Reservation.objects.get(pk=reservation_id)
	if not reservation.is_comped():
		# Let these nice people stay here for free
		reservation.comp()
	else:
		# Put the rate back to the default rate
		reservation.reset_rate()
		# if confirmed set status back to APPROVED
		if reservation.is_confirmed():
			reservation.approve()
	return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))

@house_admin_required
def DeleteBillLineItem(request, location_slug, bill_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	bill = get_object_or_404(Bill, pk=bill_id)

	if bill.is_reservation_bill():
		reservation = bill.reservationbill.reservation
		print "in delete bill line item"
		print request.POST
		item_id = int(request.POST.get("payment_id"))
		line_item = BillLineItem.objects.get(id=item_id)
		line_item.delete()
		if line_item.fee:
			reservation.suppress_fee(line_item)
		reservation.generate_bill()
		messages.add_message(request, messages.INFO, "The line item was deleted.")
		return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation.id)))
	elif bill.is_subscription_bill():
		subscription = bill.subscriptionbill.subscription
		print "in delete bill line item"
		print request.POST
		item_id = int(request.POST.get("payment_id"))
		line_item = BillLineItem.objects.get(id=item_id)
		line_item.delete()
		# subscriptions don't support external fees yet but if we add this,
		# then we should include the ability to suppress a fee. until then this won't work.
		#if line_item.fee:
		#	subscription.suppress_fee(line_item)
		subscription.generate_bill(target_date=bill.subscriptionbill.period_start)
		messages.add_message(request, messages.INFO, "The line item was deleted from the bill for %s." % (bill.subscriptionbill.period_start.strftime("%B %Y")))
		return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location.slug, subscription.id)))
	else:
		raise Exception('Unrecognized bill object')


@house_admin_required
def BillCharge(request, location_slug, bill_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	bill = get_object_or_404(Bill, pk=bill_id)

	print request.POST
	#how much to charge?
	charge_amount_dollars = Decimal(request.POST.get('charge-amount'))
	print 'request to charge user $%d' % charge_amount_dollars
	if charge_amount_dollars > bill.total_owed():
		messages.add_message(request, messages.INFO, "Cannot charge more than remaining amount owed ($%d was requested on $%d owed)" % (charge_amount_dollars, bill.total_owed()))
		return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location.slug, bill.subscriptionbill.subscription.id)))

	if bill.is_reservation_bill():
		user = bill.reservationbill.reservation.user
		reference = "%d reservation ref#%d" % (location.name, bill.reservationbill.reservation.id)
	elif bill.is_subscription_bill():
		user = bill.subscriptionbill.subscription.user
		reference = "%s subscription ref#%d.%d monthly" % (location.name, bill.subscriptionbill.subscription.id, bill.id)
	else:
		raise Exception('Unknown bill type. Cannot determine user.')

	try:
		payment = payment_gateway.charge_user(user, bill, charge_amount_dollars, reference)
	except stripe.CardError, e:
		messages.add_message(request, messages.INFO, "Charge failed with the following error: %s" % e)
		if bill.is_reservation_bill():
			return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, bill.reservationbill.reservation.id)))
		else:
			return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, bill.subscriptionbill.subscription.id)))

	if bill.is_reservation_bill():
		messages.add_message(request, messages.INFO, "The card was charged.")
		return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, bill.reservationbill.reservation.id)))
	else:
		messages.add_message(request, messages.INFO, "The card was charged. You must manually send the user their receipt. Please do so from the %s bill detail page." % bill.subscriptionbill.period_start.strftime("%B %d, %Y"))
		return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, bill.subscriptionbill.subscription.id)))


@house_admin_required
def AddBillLineItem(request, location_slug, bill_id):
	# can be used to apply a discount or a one time charge for, for example, a
	# cleaning fee.
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_object_or_404(Location, slug=location_slug)
	bill = get_object_or_404(Bill, pk=bill_id)

	reason = request.POST.get("reason")
	calculation_type = request.POST.get("calculation_type")
	if request.POST.get("discount"):
		line_item_type = "discount"
	else:
		line_item_type = "fee"
	if line_item_type == "discount":
		if calculation_type == "absolute":
			reason = "Discount: " + reason
			amount = -Decimal(request.POST.get("discount"))
		elif calculation_type == "percent":
			percent = Decimal(request.POST.get("discount"))/100
			reason = "Discount (%s%%): %s" % (percent*Decimal(100.0), reason)
			if percent < 0.0 or percent > 100.0:
				messages.add_message(request, messages.INFO, "Invalid percent value given.")
				return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))
			amount = -(bill.subtotal_amount() * percent)
		else:
			messages.add_message(request, messages.INFO, "Invalid discount type.")
			return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))
	else:
		# then it's a fee
		if calculation_type == "absolute":
			reason = "Fee: " + reason
			amount = float(request.POST.get("extra_fee"))
		elif calculation_type == "percent":
			percent = Decimal(request.POST.get("extra_fee"))/100
			reason = "Fee (%s%%): %s" % (percent*Decimal(100.0), reason)
			if percent < 0.0 or percent > 100.0:
				messages.add_message(request, messages.INFO, "Invalid percent value given.")
				return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))
			amount = (bill.subtotal_amount() * percent)
		else:
			messages.add_message(request, messages.INFO, "Invalid fee type.")
			return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))

	new_line_item = BillLineItem(description=reason, amount=amount, paid_by_house=False, custom=True)
	new_line_item.bill = bill
	new_line_item.save()
	# regenerate the bill now that we've applied some new fees (even if the
	# rate has not changed, other percentage-based fees may be affected by this
	# new line item)
	if bill.is_reservation_bill():
		reservation = bill.reservationbill.reservation
		reservation.generate_bill()
		messages.add_message(request, messages.INFO, "The %s was added." % line_item_type)
		return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation.id)))
	elif bill.is_subscription_bill():
		subscription = bill.subscriptionbill.subscription
		subscription.generate_bill(target_date=bill.subscriptionbill.period_start)
		messages.add_message(request, messages.INFO, "The %s was added to the bill for %s." % (line_item_type, bill.subscriptionbill.period_start.strftime("%B %Y")))
		return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location.slug, subscription.id)))
	else:
		raise Exception('Unrecognized bill object')

def _assemble_and_send_email(location_slug, post):
	location = get_object_or_404(Location, slug=location_slug)
	subject = post.get("subject")
	recipient = [post.get("recipient"),]
	body = post.get("body") + "\n\n" + post.get("footer")
	# TODO - This isn't fully implemented yet -JLS
	send_from_location_address(subject, body, None, recipient, location)

@house_admin_required
def ReservationSendMail(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	_assemble_and_send_email(location_slug, request.POST)
	reservation = Reservation.objects.get(id=reservation_id)
	reservation.mark_last_msg()
	messages.add_message(request, messages.INFO, "Your message was sent.")
	return HttpResponseRedirect(reverse('reservation_manage', args=(location_slug, reservation_id)))

@house_admin_required
def SubscriptionSendMail(request, location_slug, subscription_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	_assemble_and_send_email(location_slug, request.POST)
	messages.add_message(request, messages.INFO, "Your message was sent.")
	return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription_id)))

@resident_or_admin_required
def payments_today(request, location_slug):
	today = timezone.localtime(timezone.now())
	return HttpResponseRedirect(reverse('core.views.payments', args=[], kwargs={'location_slug':location_slug, 'year':today.year, 'month':today.month}))

@login_required
def PeopleDaterangeQuery(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	start_str = request.POST.get('start_date')
	end_str = request.POST.get('end_date')
	s_month, s_day, s_year = start_str.split("/")
	e_month, e_day, e_year = end_str.split("/")
	start_date = datetime.date(int(s_year), int(s_month), int(s_day))
	end_date = datetime.date(int(e_year), int(e_month), int(e_day))
	reservations_for_daterange = Reservation.objects.filter(Q(status="confirmed")).exclude(depart__lt=start_date).exclude(arrive__gte=end_date)
	recipients = []
	for r in reservations_for_daterange:
		recipients.append(r.user)
	residents = location.residents.all()
	recipients = recipients + list(residents)
	html = "<div class='btn btn-info disabled' id='recipient-list'>Your message will go to these people: "
	for person in recipients:
		info = "<a class='link-light-color' href='/people/" + person.username + "'>" + person.first_name + " " + person.last_name + "</a>, "
		html += info;

	html = html.strip(", ")

@login_required
def ReservationReceipt(request, location_slug, reservation_id):
	location = get_object_or_404(Location, slug=location_slug)
	reservation = get_object_or_404(Reservation, id=reservation_id)
	if request.user != reservation.user or location != reservation.location:
		if not request.user.is_staff:
			return HttpResponseRedirect("/404")

	# I want to render the receipt exactly like we do in the email
	htmltext = get_template('emails/receipt.html')
	c = Context({
		'today': timezone.localtime(timezone.now()),
		'user': reservation.user,
		'location': reservation.location,
		'reservation': reservation,
		'reservation_url': "https://" + Site.objects.get_current().domain + reservation.get_absolute_url()
		})
	receipt_html = htmltext.render(c)

	return render(request, 'reservation_receipt.html', {'receipt_html': receipt_html, 'reservation': reservation,
		'location': location })

def submit_payment(request, reservation_uuid, location_slug):
	reservation = Reservation.objects.get(uuid = reservation_uuid)
	location = get_object_or_404(Location, slug=location_slug)
	if request.method == 'POST':
		form = PaymentForm(request.POST, default_amount=None)
		if form.is_valid():
			# account secret key
			stripe.api_key = settings.STRIPE_SECRET_KEY

			# get the payment details from the form
			token = request.POST.get('stripeToken')
			amount = float(request.POST.get('amount'))
			pay_name = request.POST.get('name')
			pay_email = request.POST.get('email')
			comment  = request.POST.get('comment')

			pay_user = None
			try:
				pay_user = User.objects.filter(email=pay_email).first()
			except:
				pass

			# create the charge on Stripe's servers - this will charge the user's card
			charge_descr = "payment from %s (%s)." % (pay_name, pay_email)
			if comment:
				charge_descr += " Comment added: %s" % comment
			try:

				charge = payment_gateway.stripe_charge_card_third_party(reservation, amount, token, charge_descr)

				# associate payment information with reservation
				Payment.objects.create(bill=reservation.bill,
					user = pay_user,
					payment_service = "Stripe",
					payment_method = charge.card.brand,
					paid_amount = (charge.amount/100.00),
					transaction_id = charge.id,
					last4 = charge.card.last4
				)

				if reservation.bill.total_owed() <= 0.0:
					# if the reservation is all paid up, do All the Things to confirm.
					reservation.confirm()
					send_reservation_receipt(reservation, send_to=pay_email)

					# XXX TODO need a way to check if this has already been sent :/
					days_until_arrival = (reservation.arrive - datetime.date.today()).days
					if days_until_arrival <= reservation.location.welcome_email_days_ahead:
						guest_welcome(reservation)
					messages.add_message(request, messages.INFO, 'Thanks you for your payment! A receipt is being emailed to you at %s' % pay_email)
				else:
					messages.add_message(request, messages.INFO, 'Thanks you for your payment! There is now a pending amount due of $%.2f' % reservation.bill.total_owed())
					form = PaymentForm(default_amount=reservation.bill.total_owed)

			except Exception, e:
				messages.add_message(request, messages.INFO, 'Drat, there was a problem with your card. Sometimes this reflects a card transaction limit, or bank hold due to an unusual charge. Please contact your bank or credit card, or try a different card. The error returned was: <em>%s</em>' % e)
		else:
			print 'payment form not valid'
			print form.errors

	else:
		form = PaymentForm(default_amount=reservation.bill.total_owed)


	if reservation.bill.total_owed() > 0.0:
		owed_color = "text-danger"
	else:
		owed_color = "text-success"
	return render(request, "payment.html", {"r": reservation, 'location': location, 'total_owed_color': owed_color,
		'form': form, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})


@resident_or_admin_required
def payments(request, location_slug, year, month):
	t0 = time.time()
	logger.debug('payments: timing begun:')
	location = get_object_or_404(Location, slug=location_slug)
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	summary_totals = {
			'gross_rent': 0,
			'net_rent_resident': 0,
			'gross_rent_transient': 0,
			'net_rent_transient': 0,
			'hotel_tax': 0,
			'hotel_tax_percent': 0.0,
			'res_external_txs_paid': 0,
			'res_external_txs_fees': 0,

			'all_subscriptions_net': 0,
			'taxed_subscription_gross': 0,
			'untaxed_subscription_net': 0,
			'taxed_subscription_user_fees': 0,
			'sub_external_txs_paid': 0,
			'sub_external_txs_fees': 0,
		}

	##############################

	reservation_totals = {
			'count':0,
			'house_fees':0,
			'to_house':0,
			'non_house_fees':0,
			'paid_amount':0
		}

	# JKS if the reservation has bill line items that are not paid by the house
	# (so-called non_house_fees), then the amount to_house counts as transient
	# occupancy income. otherwise it counts as resident occupancy income.
	# TODO: we're essentially equating non house fees with hotel taxes. we
	# should make this explicit in some way.

	reservation_payments_this_month = Payment.objects.reservation_payments_by_location(location).filter(payment_date__gte=start, payment_date__lte=end).order_by('payment_date').reverse()
	for p in reservation_payments_this_month:
		# pull out the values we call multiple times to make this faster
		p_to_house = p.to_house()
		p_bill_non_house_fees = p.bill.non_house_fees()
		p_house_fees = p.house_fees()
		p_non_house_fees = p.non_house_fees()
		p_paid_amount = p.paid_amount

		summary_totals['gross_rent'] += p_to_house
		if p_bill_non_house_fees > 0:
			summary_totals['gross_rent_transient'] += (p_to_house + p_house_fees)
			summary_totals['net_rent_transient'] += p_to_house
			# XXX is p_non_house_fees == p_bill_non_house_fees??
			summary_totals['hotel_tax'] += p_non_house_fees
		else:
			summary_totals['net_rent_resident'] += p_to_house
		# track reservation totals
		reservation_totals['count'] = reservation_totals['count'] + 1
		reservation_totals['to_house'] = reservation_totals['to_house'] + p_to_house
		reservation_totals['non_house_fees'] = reservation_totals['non_house_fees'] + p_non_house_fees
		reservation_totals['house_fees'] = reservation_totals['house_fees'] + p_house_fees
		reservation_totals['paid_amount'] = reservation_totals['paid_amount'] + p_paid_amount
		if p.transaction_id == 'Manual':
			summary_totals['res_external_txs_paid'] += p_paid_amount
			summary_totals['res_external_txs_fees'] += p_house_fees

	not_paid_by_house = LocationFee.objects.filter(location=location).filter(fee__paid_by_house=False)
	for loc_fee in not_paid_by_house:
		summary_totals['hotel_tax_percent'] += loc_fee.fee.percentage*100

	##############################

	subscription_totals = {
			'count':0,
			'house_fees':0,
			'to_house':0,
			'user_fees':0,
			'total_paid':0 # the paid amount is to_house + user_fees + house_fees
		}

	subscription_payments_this_month = Payment.objects.subscription_payments_by_location(location).filter(payment_date__gte=start, payment_date__lte=end).order_by('payment_date').reverse()
	# house fees are fees paid by the house
	# non house fees are fees passed on to the user
	for p in subscription_payments_this_month:
		# pull out the values we call multiple times to make this faster
		to_house = p.to_house()
		user_fees = p.bill.non_house_fees() #p_bill_non_house_fees = p.bill.non_house_fees()
		house_fees = p.house_fees() #p_house_fees = p.house_fees()
		total_paid = p.paid_amount

		summary_totals['all_subscriptions_net'] += to_house
		if user_fees > 0:
			# the gross value of subscriptions that were taxed/had user fees
			# applied are tracked as a separate line item for assistance with
			# later accounting
			summary_totals['taxed_subscription_gross'] += to_house + user_fees
			summary_totals['taxed_subscription_net'] += to_house
			summary_totals['taxed_subscription_user_fees'] += user_fees
		else:
			summary_totals['untaxed_subscription_net'] += to_house

		# track subscription totals
		subscription_totals['count'] = subscription_totals['count'] + 1
		subscription_totals['to_house'] = subscription_totals['to_house'] + to_house
		subscription_totals['user_fees'] = subscription_totals['user_fees'] + user_fees
		subscription_totals['house_fees'] = subscription_totals['house_fees'] + house_fees
		subscription_totals['total_paid'] = subscription_totals['total_paid'] + total_paid
		if p.transaction_id == 'Manual':
			summary_totals['sub_external_txs_paid'] += total_paid
			summary_totals['sub_external_txs_fees'] += house_fees



	##############################

	summary_totals['res_total_transfer'] = (
		summary_totals['gross_rent']
		+ summary_totals['hotel_tax']
		- summary_totals['res_external_txs_paid']
		- summary_totals['res_external_txs_fees']
	)

	summary_totals['sub_total_transfer'] = (
		summary_totals['all_subscriptions_net']
		+ summary_totals['taxed_subscription_user_fees']
		- summary_totals['sub_external_txs_paid']
		- summary_totals['sub_external_txs_fees']
	)

	summary_totals['total_transfer'] = summary_totals['res_total_transfer'] + summary_totals['sub_total_transfer']
	summary_totals['gross_reservations'] = summary_totals['gross_rent_transient'] + summary_totals['net_rent_resident']
	summary_totals['gross_subscriptions'] = summary_totals['taxed_subscription_gross'] + summary_totals['untaxed_subscription_net']

	t1 = time.time()
	dt = t1-t0
	logger.debug('payments: timing ended. time taken:')
	logger.debug(dt)
	return render(request, "payments.html", {'reservation_payments': reservation_payments_this_month,
		'summary_totals': summary_totals, 'subscription_payments': subscription_payments_this_month,
		'subscription_totals': subscription_totals, 'reservation_totals':reservation_totals,
		'location': location, 'this_month':start, 'previous_date':prev_month, 'next_date':next_month})

# ******************************************************
#           registration and login callbacks and views
# ******************************************************

def process_unsaved_reservation(request):
	logger.debug("in process_unsaved_reservation")
	if request.session.get('reservation'):
		logger.debug('found reservation')
		logger.debug(request.session['reservation'])
		details = request.session.pop('reservation')
		new_res = Reservation(
				arrive = datetime.date(details['arrive']['year'], details['arrive']['month'], details['arrive']['day']),
				depart = datetime.date(details['depart']['year'], details['depart']['month'], details['depart']['day']),
				location = Location.objects.get(id=details['location']['id']),
				resource = Resource.objects.get(id=details['resource']['id']),
				purpose = details['purpose'],
				arrival_time = details['arrival_time'],
				comments = details['comments'],
				user = request.user,
				)
		new_res.save()
		new_res.reset_rate()
		new_res.generate_bill()
		logger.debug('new reservation %d saved.' % new_res.id)
		new_reservation_notify(new_res)
		# we can't just redirect here because the user doesn't get logged
		# in. so save the reservaton ID and redirect below.
		request.session['new_res_redirect'] = {'res_id': new_res.id, 'location_slug': new_res.location.slug}
	else:
		logger.debug("no reservation found")
	return


def user_login(request):
	logger.debug('in user_login')
	next_page = None
	if 'next' in request.GET:
		next_page = request.GET['next']

	username = password = ''
	if request.POST:
		username = request.POST['username']
		# JKS this is a bit janky. this is because we use this view both after
		# the user registration or after the login view, which themselves use
		# slightly different forms.
		if 'password' in request.POST:
			password = request.POST['password']
		elif 'password2' in request.POST:
			password = request.POST['password2']
		if 'next' in request.POST:
			next_page = request.POST['next']

		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)

			process_unsaved_reservation(request)
			# if there was a pending reservation redirect to the reservation page
			if request.session.get('new_res_redirect'):
				res_id = request.session['new_res_redirect']['res_id']
				location_slug = request.session['new_res_redirect']['location_slug']
				request.session.pop('new_res_redirect')
				messages.add_message(request, messages.INFO, 'Thank you! Your reservation has been submitted. Please allow us up to 24 hours to respond.')
				return HttpResponseRedirect(reverse('reservation_detail', args=(location_slug, res_id)))

			# this is where they go on successful login if there is not pending reservation
			if not next_page or len(next_page) == 0 or "logout" in next_page:
				next_page = "/"
			return HttpResponseRedirect(next_page)

	# redirect to the login page if there was a problem
	return render(request, 'registration/login.html', context_instance=RequestContext(request))


def register(request):
	if request.session.get('reservation'):
		reservation = request.session.get('reservation')
	else:
		reservation = None
	if request.method == "POST":
		profile_form = UserProfileForm(request.POST, request.FILES)
		if profile_form.is_valid():
			user = profile_form.save()
			request.POST['username'] = user.username
			return user_login(request)
		else:
			print 'profile form contained errors:'
			print profile_form.errors
	else:
		if request.user.is_authenticated():
			messages.add_message(request, messages.INFO, 'You are already logged in. Please <a href="/people/logout">log out</a> to create a new account')
			return HttpResponseRedirect(reverse('user_detail', args=(request.user.username,)))
		profile_form = UserProfileForm()
	all_users = User.objects.all()
	return render(request, 'registration/registration_form.html', { 'form': profile_form, 'reservation': reservation, 'all_users':all_users})

@login_required
def UserEdit(request, username):
	profile = UserProfile.objects.get(user__username=username)
	user = User.objects.get(username=username)
	if not (request.user.is_authenticated() and request.user.id == user.id):
		messages.add_message(request, messages.INFO, "You cannot edit this profile")
		return HttpResponseRedirect('/404')

	if request.method == "POST":
		profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
		if profile_form.is_valid():
			user = profile_form.save()
			messages.add_message(request, messages.INFO, "Your profile has been updated.")
			return HttpResponseRedirect("/people/%s" % user.username)
		else:
			print 'profile form contained errors:'
			print profile_form.errors
	else:
		profile_form = UserProfileForm(instance=profile)
	if profile.image:
		has_image = True
	else:
		has_image = False
	return render(request, 'registration/registration_form.html', {'form': profile_form, 'has_image': has_image, 'existing_user': True})


@house_admin_required
def SubscriptionManageCreate(request, location_slug):
	if request.method == 'POST':
		location = get_object_or_404(Location, slug=location_slug)
		notify = request.POST.get('email_announce');
		try:
			username = request.POST.get('username');
			subscription_user = User.objects.get(username=username)
		except:
			messages.add_message(request, messages.INFO, "There is no user with the username %s" % username)
			return HttpResponseRedirect(reverse('reservation_manage_create', args=(location.slug,)))

		form = AdminSubscriptionForm(request.POST)
		if form.is_valid():
			subscription = form.save(commit=False)
			subscription.location = location
			subscription.user = subscription_user
			subscription.created_by = request.user
			subscription.save()
			subscription.generate_all_bills()
			if notify:
				admin_new_subscription_notify(subscription)
			messages.add_message(request, messages.INFO, "The subscription for %s %s was created." % (subscription.user.first_name, subscription.user.last_name))
			return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location.slug, subscription.id)))
		else:
			logger.debug('the form had errors')
			logger.debug(form.errors)
			logger.debug(request.POST)

	else:
		form = AdminSubscriptionForm()
	all_users = User.objects.all().order_by('username')
	return render(request, 'subscription_manage_create.html', {'form': form, 'all_users': all_users})


@house_admin_required
def SubscriptionsManageList(request, location_slug):
	location = get_object_or_404(Location, slug=location_slug)
	active = Subscription.objects.active_subscriptions().filter(location=location).order_by('-start_date')
	inactive = Subscription.objects.inactive_subscriptions().filter(location=location).order_by('-end_date')
	return render(request, 'subscriptions_list.html', {"active": active, "inactive": inactive, 'location': location})

@house_admin_required
def SubscriptionManageDetail(request, location_slug, subscription_id):
	location = get_object_or_404(Location, slug=location_slug)
	subscription = get_object_or_404(Subscription, id=subscription_id)
	user = User.objects.get(username=subscription.user.username)
	domain = Site.objects.get_current().domain
	logger.debug("SubscriptionManageDetail:")

	email_forms = []
	email_templates_by_name = []

	emails = EmailTemplate.objects.filter(context='subscription')
	for email_template in emails:
		form = SubscriptionEmailTemplateForm(email_template, subscription, location)
		email_forms.append(form)
		email_templates_by_name.append(email_template.name)

	# Pull all the reservation notes for this person
	if 'note' in request.POST:
		note = request.POST['note']
		if note:
			SubscriptionNote.objects.create(subscription=subscription, created_by=request.user, note=note)
			# The Right Thing is to do an HttpResponseRedirect after a form
			# submission, which clears the POST request data (even though we
			# are redirecting to the same view)
			subscription_note_notify(subscription)
			return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription_id)))
	subscription_notes = SubscriptionNote.objects.filter(subscription=subscription)

	# Pull all the user notes for this person
	if 'user_note' in request.POST:
		note = request.POST['user_note']
		if note:
			UserNote.objects.create(user=user, created_by=request.user, note=note)
			# The Right Thing is to do an HttpResponseRedirect after a form submission
			return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, reservation_id)))
	user_notes = UserNote.objects.filter(user=user)

	return render(request, 'subscription_manage.html', {
		"s": subscription,
		"user_notes": user_notes,
		"subscription_notes": subscription_notes,
		"email_forms" : email_forms,
		"email_templates_by_name" : email_templates_by_name,
		"domain": domain, 'location': location,
	})

@house_admin_required
def SubscriptionManageUpdateEndDate(request, location_slug, subscription_id):
	location = get_object_or_404(Location, slug=location_slug)
	subscription = Subscription.objects.get(id=subscription_id)
	logger.debug(request.POST)

	new_end_date = None # an empty end date is an ongoing subscription.
	old_end_date = subscription.end_date
	if request.POST.get("end_date"):
		new_end_date = datetime.datetime.strptime(request.POST['end_date'],'%m/%d/%Y').date()
		# disable setting the end date earlier than any recorded payments for associated bills (even partial payments)
		most_recent_paid = subscription.last_paid(include_partial=True)

		# careful, a subscription which has not had any bills generated yet
		# will have a paid_until value of None but is not problematic to change
		# the date.
		if most_recent_paid and new_end_date < most_recent_paid:
			messages.add_message(request, messages.INFO, "Error! This subscription already has payments past the requested end date. Please choose an end date after %s." % most_recent_paid.strftime("%B %d, %Y"))
			return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription_id)))

		if old_end_date and new_end_date == old_end_date:
			messages.add_message(request, messages.INFO, "The new end date was the same.")
			return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription_id)))

	subscription.update_for_end_date(new_end_date)
	messages.add_message(request, messages.INFO, "Subscription end date updated.")
	return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription_id)))

@house_admin_required
def SubscriptionManageGenerateAllBills(request, location_slug, subscription_id):
	subscription = get_object_or_404(Subscription, pk=subscription_id)
	subscription.generate_all_bills()
	messages.add_message(request, messages.INFO, "Bills up to the current period were generated.")
	return HttpResponseRedirect(reverse('subscription_manage_detail', args=(location_slug, subscription.id)))
