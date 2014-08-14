from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import transaction
from PIL import Image
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from registration import signals
import registration
from core.forms import ReservationForm, UserProfileForm, EmailTemplateForm, PaymentForm
from django.core import urlresolvers
from django.contrib import messages
from django.conf import settings
from core.decorators import house_admin_required
from django.db.models import Q
from core.models import UserProfile, Reservation, Room, Payment, EmailTemplate, Location, LocationFee
from core.tasks import guest_welcome
import uuid, base64, os
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from gather.tasks import published_events_today_local, events_pending
from gather.forms import NewUserForm
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe
from datetime import date, datetime, timedelta
import json, datetime, stripe 
from reservation_calendar import GuestCalendar
from emails import send_receipt, new_reservation_notify, updated_reservation_notify, send_from_location_address
from django.core.urlresolvers import reverse
from core.models import get_location
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Context
import logging

logger = logging.getLogger(__name__)

def location(request, location_slug):
	location = my_object = get_object_or_404(Location, slug=location_slug)

	today = timezone.localtime(timezone.now())

	if request.user.is_authenticated():
		current_user = request.user
	else:
		current_user = None
	
	# pull out all reservations in the coming month
	coming_month_res = (
			Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
			.filter(location=location)
			.exclude(depart__lt=today)
			.exclude( arrive__gt=today+datetime.timedelta(days=30))
		)
	people_in_coming_month = []
	for r in coming_month_res:
		# check for duplicates, add if not already there.
		if r.user not in people_in_coming_month:
			people_in_coming_month.append(r.user)

	# add residents to the list of people in the house in the coming month. 
	residents = list(location.residents.all())
	for r in residents:
		# check for duplicates, add if not already there.
		if r not in people_in_coming_month:
			people_in_coming_month.append(r)

	# Add all the people from events too if we have gather installed
	events = None
	if 'gather' in settings.INSTALLED_APPS:
		from gather.models import Event
		events = Event.objects.upcoming(upto=5, current_user=current_user, location=location)
		coming_month_events = (
				Event.objects.filter(status="live") 
				.filter(location=location)
				.exclude(end__lt=today)
				.exclude( start__gte=today+datetime.timedelta(days=30))
			)
		for e in coming_month_events:
			# check for duplicates, add if not already there.
			for u in e.organizers.all():
				if u not in people_in_coming_month:
					people_in_coming_month.append(u)

	if not request.user.is_authenticated():
		new_user_form = NewUserForm()
	else:
		new_user_form = None

	return render(request, "landing.html", {'location': location, 'people_in_coming_month': people_in_coming_month, 'events': events, 'new_user_form': new_user_form})

def about(request, location_slug):
	location = get_location(location_slug)
	return render(request, "location_about.html", {'location_about_text': location.about_page, 'location': location})

def guest_rooms(request, location_slug):
	location = get_location(location_slug)
	rooms = location.guest_rooms()
	return render(request, "location_rooms.html", {'rooms': rooms, 'location': location})

def view_room(request, location_slug, room_id):
	location = get_location(location_slug)
	room = get_object_or_404(Room, id=room_id)
	today = timezone.localtime(timezone.now())
	month = request.GET.get("month")
	year = request.GET.get("year")
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	return render(request, "room.html", {'room': room, 'location': location, "next_month": next_month, "prev_month": prev_month})

def residents(request, location_slug):
	location = get_location(location_slug)
	residents = location.residents.all()
	return render(request, "location_residents.html", {'residents': residents, 'location': location})

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
	location = get_location(location_slug)
	# get all the reservations that intersect today (including those departing
	# and arriving today)
	today = timezone.now()
	reservations_today = Reservation.objects.filter(Q(status="confirmed") | Q(status="approved")).exclude(depart__lt=today).exclude(arrive__gt=today)
	guests_today = []
	for r in reservations_today:
		guests_today.append(r.user)
	residents = location.residents.all()
	people_today = guests_today + list(residents)

	events_today = published_events_today_local()
	return render(request, "today.html", {'people_today': people_today, 'events_today': events_today})

@house_admin_required
def occupancy(request, location_slug):
	location = get_location(location_slug)
	today = datetime.date.today()
	month = request.GET.get("month")
	year = request.GET.get("year")

	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	# note the day parameter is meaningless
	report_date = datetime.date(year, month, 1) 
	reservations = Reservation.objects.filter(location=location).filter(status="confirmed").exclude(depart__lt=start).exclude(arrive__gt=end)

	person_nights_data = []
	total_person_nights = 0
	total_income = 0
	total_income_shared = 0
	total_income_private = 0
	total_comped_nights = 0
	total_comped_income = 0
	total_shared_nights = 0
	total_private_nights = 0
	unpaid_total = 0
	room_income = {}
	income_for_this_month = 0
	income_for_future_months = 0
	income_from_past_months = 0
	income_for_past_months = 0
	paid_rate_discrepancy = 0
	payment_discrepancies = []
	paid_amount_missing = []

	payments_this_month = Payment.objects.filter(reservation__location=location).filter(payment_date__gte=start).filter(payment_date__lte=end)
	for r in payments_this_month:
		nights_before_this_month = datetime.timedelta(0)
		nights_after_this_month = datetime.timedelta(0)
		if r.reservation.arrive < start and r.reservation.depart < start:
			# all nights for this reservation were in a previous month
			nights_before_this_month = (r.reservation.depart - r.reservation.arrive)
		
		elif r.reservation.arrive < start and r.reservation.depart <= end:
			# only nights this month, don't need to calculate this here because
			# it's calculated below. 
			nights_before_this_month = (start - r.reservation.arrive)
		
		elif r.reservation.arrive >= start and r.reservation.depart <= end:
			# only nights this month, don't need to calculate this here because
			# it's calculated below. 
			continue
		
		elif r.reservation.arrive >= start and r.reservation.arrive <= end and r.reservation.depart > end:
			nights_after_this_month = (r.reservation.depart - end)
		
		elif r.reservation.arrive > end:  
			nights_after_this_month = (r.reservation.depart - r.reservation.arrive)

		elif r.reservation.arrive < start and r.reservation.depart > end:  
			# there are some days paid for this month that belong to the previous month
			nights_before_this_month = (start - r.reservation.arrive)
			nights_after_this_month = (r.reservation.depart - end)
		
		income_for_future_months += nights_after_this_month.days*(r.paid_amount/(r.reservation.depart - r.reservation.arrive).days)
		income_for_past_months += nights_before_this_month.days*(r.paid_amount/(r.reservation.depart - r.reservation.arrive).days)

	for r in reservations:
		comp = False
		if r.arrive >=start and r.depart <= end:
			nights_this_month = (r.depart - r.arrive).days
		elif r.arrive <=start and r.depart >= end:
			nights_this_month = (end - start).days
		elif r.arrive < start:
			nights_this_month = (r.depart - start).days
		elif r.depart > end:
			nights_this_month = (end - r.arrive).days
		# if it's the first of the month and the person left on the 1st, then
		# that's actuallu 0 days this month which we don't need to include.
		if nights_this_month == 0:
			continue
		# get_rate grabs the custom rate if it exists, else default rate as
		# defined in the room definition.
		rate = r.rate
		if r.is_comped():
			total_comped_nights += nights_this_month
			total_comped_income += nights_this_month*r.default_rate()
			comp = True
			unpaid = False
		else:
			total_income += nights_this_month*rate
			this_room_income = room_income.get(r.room.name, 0)
			this_room_income += rate*nights_this_month
			room_income[r.room.name] = this_room_income

			# If there are payments, calculate the payment rate
			if r.payments():
				paid_rate = r.total_paid() / r.total_nights()
				if paid_rate != rate:
					print "reservation %d has paid rate = $%d and rate set to $%d"
					paid_rate_discrepancy += nights_this_month * (paid_rate - rate)
					payment_discrepancies.append(r.id)

			# XXX I don't understand this part.  I'm going to just put the payment amount on this month
			# and move on for now.  --JLS
			#if r.is_paid():
			#	if (r.payment.payment_date and r.payment.payment_date < start):
			#		income_from_past_months += nights_this_month*(r.payment.paid_amount/(r.depart - r.arrive).days)
			#	else:
			#		# if there's no payment date but the reservation is marked
			#		# as paid, the payment was probably manually entered. since
			#		# we have no knowledge of when the payment was issued,
			#		# applying it to this month seems like a reasonable guess. 
			#		# XXX todo would be nice to highlight these items somehow. 
			#		# TODO This should not happen anymore.  Date defaults to today and amount defaults to 0 --JLS
			#		if r.payment.paid_amount:
			#			income_for_this_month += nights_this_month*(r.payment.paid_amount/(r.depart - r.arrive).days) 
			#		else:
			#			paid_amount_missing.append(r.id)
			if r.is_paid():
				income_for_this_month += r.total_paid()
				unpaid = False
			else:
				unpaid_total += r.total_owed()
				unpaid = True

		person_nights_data.append({
			'reservation': r,
			'nights_this_month': nights_this_month,
			'room': r.room.name,
			'rate': rate,
			'total': nights_this_month*rate,
			'comp': comp,
			'unpaid': unpaid
		})
		total_person_nights += nights_this_month
		if r.room.shared:
			total_shared_nights += nights_this_month
			if not r.is_comped():
				total_income_shared += nights_this_month*rate
		else:
			total_private_nights += nights_this_month
			if not r.is_comped():
				total_income_private += nights_this_month*rate

	total_income_this_month = income_for_this_month + income_from_past_months
	total_income_during_month = income_for_this_month + income_for_future_months
	total_by_rooms = sum(room_income.itervalues())

	return render(request, "occupancy.html", {"data": person_nights_data, 'location': location,
		'total_nights':total_person_nights, 'total_income':total_income, 'unpaid_total': unpaid_total,
		'total_shared_nights': total_shared_nights, 'total_private_nights': total_private_nights,
		'total_comped_income': total_comped_income, 'total_comped_nights': total_comped_nights,
		"next_month": next_month, "prev_month": prev_month, "total_income_shared": total_income_shared,
		"total_income_private": total_income_private, "report_date": report_date, 'room_income':room_income, 
		'income_for_this_month': income_for_this_month, 'income_for_future_months':income_for_future_months, 
		'income_from_past_months': income_from_past_months, 'income_for_past_months':income_for_past_months, 
		'total_income_this_month':total_income_this_month, 'total_by_rooms': total_by_rooms, 
		'paid_rate_discrepancy': paid_rate_discrepancy, 'payment_discrepancies': payment_discrepancies, 
		'total_income_during_month': total_income_during_month, 'paid_amount_missing':paid_amount_missing })

@login_required
def calendar(request, location_slug):
	location = get_location(location_slug)
	today = timezone.localtime(timezone.now())
	month = request.GET.get("month")
	year = request.GET.get("year")

	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	report_date = datetime.date(year, month, 1) 

	reservations = (Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
		.filter(location=location).exclude(depart__lt=start).exclude(arrive__gt=end).order_by('arrive'))
	
	# create the calendar object
	guest_calendar = GuestCalendar(reservations, year, month, location).formatmonth(year, month)

	return render(request, "calendar.html", {'reservations': reservations, 
		'calendar': mark_safe(guest_calendar), "next_month": next_month, 
		"prev_month": prev_month, "report_date": report_date, 'location': location })


def room_cal_request(request, location_slug, room_id):
	location = get_location(location_slug)
	room = Room.objects.get(id=room_id)
	month = int(request.GET.get("month"))
	year = int(request.GET.get("year"))
	cal_html = room.availability_calendar_html(month=month, year=year)
	#print 'here is the calendar info for %s' % room.name
	#print cal_html
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	link_html = '''
		<a class="room-cal-req" href="%s?month=%d&year=%d">Previous</a> | 
		<a class="room-cal-req" href="%s?month=%d&year=%d">Next</a>
	''' % (reverse(room_cal_request, args=(location.slug, room.id)), prev_month.month, prev_month.year, 
			reverse(room_cal_request, args=(location.slug, room.id)), next_month.month, next_month.year)
	return HttpResponse(cal_html+link_html)

def stay(request, location_slug):
	location = get_location(location_slug)

	rooms = location.guest_rooms()
	today = timezone.localtime(timezone.now())
	month = request.GET.get("month")
	year = request.GET.get("year")
	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	return render(request, "location_stay.html", {'location_stay_text': location.stay_page, 'rooms':rooms, "next_month": next_month, 
		"prev_month": prev_month, 'location': location})


def GenericPayment(request, location_slug):
	if request.method == 'POST':
		form = PaymentForm(request.POST)
		if form.is_valid():
			# account secret key 
			stripe.api_key = settings.STRIPE_SECRET_KEY
			
			# get the payment details from the form
			token = request.POST.get('stripeToken')
			charge_amt = int(request.POST.get('amount'))
			pay_name = request.POST.get('name')
			pay_email = request.POST.get('email')
			comment  = request.POST.get('comment')

			# create the charge on Stripe's servers - this will charge the user's card
			charge_descr = "payment from %s (%s)." % (pay_name, pay_email)
			if comment:
				charge_descr += " comment: %s" % comment
			charge = stripe.Charge.create(
					amount=charge_amt*100, # convert dollars to cents
					currency="usd",
					card=token,
					description= charge_descr
			)

			# TODO error handling if charge does not succeed
			return HttpResponseRedirect("/thanks")
	else:
		form = PaymentForm()		
	return render(request, "payment.html", {'form': form, 
		'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})


def thanks(request):
	# TODO generate receipt
	return render(request, "thanks.html")

def logout(request, location_slug = None):
	logout(request)
	messages.add_message(request, messages.INFO, 'You have been logged out.')
	return HttpResponseRedirect("/")

@login_required
def ListUsers(request):
	users = User.objects.filter(is_active=True)
	return render(request, "user_list.html", {"users": users})

@login_required
def GetUser(request, username):
	try:
		user = User.objects.get(username=username)
	except:
		messages.add_message(request, messages.INFO, 'There is no user with that username.')
		return HttpResponseRedirect('/404')

	reservations = Reservation.objects.filter(user=user).exclude(status='deleted')
	past_reservations = []
	upcoming_reservations = []
	for reservation in reservations:
		if reservation.arrive >= datetime.date.today():
			upcoming_reservations.append(reservation)
		else:
			past_reservations.append(reservation)
	return render(request, "user_details.html", {"u": user, 
		"past_reservations": past_reservations, "upcoming_reservations": upcoming_reservations, 
		"stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY})

def location_list(request):
	locations = Location.objects.all()
	return render(request, "location_list.html", {"locations": locations})

@login_required
def CheckRoomAvailability(request, location_slug):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	location=get_location(location_slug)
	arrive_str = request.POST.get('arrive')
	depart_str = request.POST.get('depart')
	a_month, a_day, a_year = arrive_str.split("/")
	d_month, d_day, d_year = depart_str.split("/")
	arrive = datetime.date(int(a_year), int(a_month), int(a_day))
	depart = datetime.date(int(d_year), int(d_month), int(d_day))
	availability_table = Room.objects.availability(arrive, depart, location)
	# all rooms should have an associated list of the same length that covers
	# all days, so just grab the dates from any one of them (they are already
	# sorted).
	per_date_avail = availability_table[availability_table.keys()[0]]
	dates = [tup[0] for tup in per_date_avail]
	available_reservations = {}
	# Create some mock reservations for each available room so we can generate the bill
	for room in Room.objects.free(arrive, depart, location):
		reservation = Reservation(id=-1, room=room, arrive=arrive, depart=depart, location=location)
		bill_line_items = reservation.generate_bill(delete_old_items=False, save=False)
		total = 0
		for item in bill_line_items:
			if not item.paid_by_house:
				total = total + item.amount
		nights = reservation.total_nights()
		available_reservations[room] = {'reservation':reservation, 'bill_line_items':bill_line_items, 'nights':nights, 'total':total}

	return render(request, "snippets/availability_calendar.html", {"availability_table": availability_table, "dates": dates, 
		'available_reservations': available_reservations, })


@login_required(login_url='registration_register')
def ReservationSubmit(request, location_slug):
	location=get_location(location_slug)
	if request.method == 'POST':
		#print request.POST
		#form = get_reservation_form_for_perms(request, post=True, instance=False)
		form = ReservationForm(location, request.POST)
		if form.is_valid():
			reservation = form.save(commit=False)
			reservation.user = request.user
			reservation.location = location
			reservation.save()
			# Resetting the rate will also generate a bill
			reservation.reset_rate()
			new_reservation_notify(reservation)
			messages.add_message(request, messages.INFO, 'Thanks! Your reservation was submitted. You will receive an email when it has been reviewed. Please <a href="/people/%s/edit/">update your profile</a> if your projects or other big ideas have changed since your last visit.<br><br>You can still modify your reservation.' % reservation.user.username)			
			return HttpResponseRedirect(reverse('reservation_detail', args=(location_slug, reservation.id)))
		else:
			print form.errors
	# GET request
	else: 
		#form = get_reservation_form_for_perms(request, post=False, instance=False)
		form = ReservationForm(location)
	# pass the rate for each room to the template so we can update the cost of
	# a reservation in real time. 
	rooms = Room.objects.all()
	room_list = {}
	for room in rooms:
		room_list[room.name] = room.default_rate
	room_list = json.dumps(room_list)
	return render(request, 'reservation.html', {'form': form, "room_list": room_list, 
		'max_days': location.max_reservation_days, 'location': location })


@login_required
def ReservationDetail(request, reservation_id, location_slug):
	location = get_location(location_slug)
	try:
		reservation = Reservation.objects.get(id=reservation_id)
		if not reservation:
			raise Reservation.DoesNotExist
	except Reservation.DoesNotExist:
		msg = 'The reservation you requested do not exist'
		messages.add_message(request, messages.ERROR, msg)
		return HttpResponseRedirect('/404')
	else:
		if reservation.arrive >= datetime.date.today():
			past = False
		else:
			past = True
		if reservation.is_paid():
			paid = True
		else:
			paid = False
		return render(request, "reservation_detail.html", {"reservation": reservation, "past":past, 'location': location,
			"stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY, "paid": paid, "contact" : location.from_email()})

@login_required
def UserEdit(request, username):
	profile = UserProfile.objects.get(user__username=username)
	user = User.objects.get(username=username)
	if request.user.is_authenticated() and request.user.id == user.id:
		if request.method == "POST":
			profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
			if profile_form.is_valid(): 
				updated_user = profile_form.save()
				profile = updated_user.profile

				print "request data: image field"
				img_data = request.POST.get("image")
				if img_data:
					#print img_data
					img_data = base64.b64decode(img_data)
					filename = "%s.png" % uuid.uuid4()
					# XXX make the upload path a fixed setting in models, since it's
					# referenced in three places
					upload_path = "data/avatars/%s/" % user.username
					upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
					if not os.path.exists(upload_abs_path):
						os.makedirs(upload_abs_path)
					full_file_name = os.path.join(upload_abs_path, filename)
					with open(full_file_name, 'wb') as f:
						f.write(img_data)
						f.close()
					profile.image = full_file_name

				profile.save()
				client_msg = "Your profile has been updated."
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect("/people/%s" % updated_user.username)
			else:
				print profile_form.errors
		else:
			profile_form = UserProfileForm(instance=profile)		
		if profile.image:
			has_image = True
		else:
			has_image = False
		#print 'profile image already?'
		#print has_image
		return render(request, 'registration/registration_form.html', {'form': profile_form, 'has_image': has_image, 'existing_user': True})
	return HttpResponseRedirect("/")

@login_required
def UserAddCard(request, username):
	''' Adds a card from either the reservation page or the user profile page.
	Displays success or error message and returns user to originating page.'''

	user = User.objects.get(username=username)
	if not request.method == 'POST' or request.user != user:
		return HttpResponseRedirect('/404')

	token = request.POST.get('stripeToken')
	if not token:
		messages.add_message(request, messages.INFO, "No credit card information was given.")
		return HttpResponseRedirect("/people/%s" % username)

	reservation_id = request.POST.get('res-id')
	if reservation_id:
		reservation = Reservation.objects.get(id=reservation_id)

	stripe.api_key = settings.STRIPE_SECRET_KEY

	try:
		customer = stripe.Customer.create(
			card=token,
			description=user.email
		)
		profile = user.profile
		profile.customer_id = customer.id
		profile.save()

		# if the card is being added from the reservation page, then charge the card
		if reservation_id:
			try:
				# charges card, saves payment details and emails a receipt to
				# the user
				reservation.charge_card()
				send_receipt(reservation)
				reservation.confirm()
				days_until_arrival = (reservation.arrive - datetime.date.today()).days
				if days_until_arrival < reservation.location.welcome_email_days_ahead:
					guest_welcome(reservation)
				messages.add_message(request, messages.INFO, 'Thank you! Your payment has been processed and a receipt emailed to you at %s. You will receive an email with house access information and other details %d days before your arrival.' % (user.email, reservation.location.welcome_email_days_ahead))
				return HttpResponseRedirect("/reservation/%d" % int(reservation_id))
			except stripe.CardError, e:
				raise stripe.CardError(e)
		# if the card is being added from the user profile page, just save it. 
		else:
			messages.add_message(request, messages.INFO, 'Thanks! Your card has been saved.')
			return HttpResponseRedirect("/people/%s" % username)
	except stripe.CardError, e:
		messages.add_message(request, messages.ERROR, 'Drat, it looks like there was a problem with your card: <em>%s</em>. Please try again.' % (e))
		if reservation_id:
			return HttpResponseRedirect("/reservation/%d" % int(reservation_id))
		else:
			return HttpResponseRedirect("/people/%s" % username)

def UserDeleteCard(request, username):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	profile = UserProfile.objects.get(user__username=username)
	profile.customer_id = None
	profile.save()
	
	messages.add_message(request, messages.INFO, "Card deleted.")
	return HttpResponseRedirect("/people/%s" % profile.user.username)



@login_required
def ReservationEdit(request, reservation_id, location_slug):
	logger.debug("Entering ReservationEdit")
	
	location = get_location(location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	# need to pull these dates out before we pass the instance into
	# the ReservationForm, since it (apparently) updates the instance 
	# immediately (which is weird, since it hasn't validated the form 
	# yet!)
	original_arrive = reservation.arrive
	original_depart = reservation.depart
	original_room = reservation.room
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
				logger.debug("room: %s, original: %s" % (reservation.room, original_room))
				if (not reservation.is_pending() and (reservation.arrive != original_arrive or 
					reservation.depart != original_depart or reservation.room != original_room )):
					logger.debug("reservation room or date was changed. updating status.")
					reservation.pending()
					# notify house_admins by email
					updated_reservation_notify(reservation)
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
			'location': location })

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
			reservation.charge_card()
			reservation.confirm()
			send_receipt(reservation)
			# if reservation start date is sooner than WELCOME_EMAIL_DAYS_AHEAD,
			# need to send them house info manually. 
			days_until_arrival = (reservation.arrive - datetime.date.today()).days
			if days_until_arrival < reservation.location.welcome_email_days_ahead:
				guest_welcome(reservation)
			messages.add_message(request, messages.INFO, 'Thank you! Your payment has been received and a receipt emailed to you at %s' % reservation.user.email)
		except stripe.CardError, e:
			messages.add_message(request, messages.ERROR, 'Drat, it looks like there was a problem with your card: <em>%s</em>. Please try again.' % (e))

	return HttpResponseRedirect("/reservation/%s" % reservation_id)

@login_required
def ReservationCancel(request, reservation_id, location_slug):
	if not request.method == "POST":
		return HttpResponseRedirect("/404")

	location = get_location(location_slug)
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

@login_required
def ReservationReceipt(request, location_slug, reservation_id):
	location = get_location(location_slug)
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
		}) 
	receipt_html = htmltext.render(c)

	return render(request, 'reservation_receipt.html', {'receipt_html': receipt_html, 'reservation': reservation, 
		'location': location })

@login_required
def PeopleDaterangeQuery(request, location_slug):
	location = get_location(location_slug)
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
	html += "</div>"
	return HttpResponse(html)

# ******************************************************
#           reservation management views
# ******************************************************

@house_admin_required
def ReservationManageList(request, location_slug):
	location = get_location(location_slug)
	pending = Reservation.objects.filter(location=location).filter(status="pending")
	approved = Reservation.objects.filter(location=location).filter(status="approved")
	confirmed = Reservation.objects.filter(location=location).filter(status="confirmed")
	canceled = Reservation.objects.filter(location=location).exclude(status="confirmed").exclude(status="approved").exclude(status="pending")
	return render(request, 'reservation_list.html', {"pending": pending, "approved": approved, 
		"confirmed": confirmed, "canceled": canceled, 'location': location})


@house_admin_required
def ReservationManage(request, location_slug, reservation_id):
	location = get_location(location_slug)
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
	emails = EmailTemplate.objects.filter(Q(shared=True) | Q(creator=request.user))
	email_forms = []
	email_templates_by_name = []
	for email_template in emails:
		form = EmailTemplateForm(email_template, reservation, location)
		email_forms.append(form)
		email_templates_by_name.append(email_template.name)
	
	availability = Room.objects.availability(reservation.arrive, reservation.depart, location)
	free = Room.objects.free(reservation.arrive, reservation.depart, location)
	per_date_avail = availability[availability.keys()[0]]
	dates = [tup[0] for tup in per_date_avail]
	if reservation.room in free:
		room_has_availability = True
	else:
		room_has_availability = False

	return render(request, 'reservation_manage.html', {
		"r": reservation, 
		"past_reservations":past_reservations, 
		"upcoming_reservations": upcoming_reservations,
		"email_forms" : email_forms,
		"email_templates_by_name" : email_templates_by_name,
		"days_before_welcome_email" : location.welcome_email_days_ahead,
		"room_has_availability" : room_has_availability,
		"avail": availability, "dates": dates,
		"domain": domain, 'location': location,
	})


@house_admin_required
def ReservationManageUpdate(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	location = get_location(location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	reservation_action = request.POST.get('reservation-action')
	try:
		if reservation_action == 'set-tentative':
			reservation.approve()
		elif reservation_action == 'set-confirm':
			reservation.confirm()
			days_until_arrival = (reservation.arrive - datetime.date.today()).days
			if days_until_arrival < location.welcome_email_days_ahead:
				guest_welcome(reservation)
		elif reservation_action == 'set-comp':
			reservation.comp()
		elif reservation_action == 'res-charge-card':
			try:
				reservation.charge_card()
				reservation.confirm()
				send_receipt(reservation)
				days_until_arrival = (reservation.arrive - datetime.date.today()).days
				if days_until_arrival < location.welcome_email_days_ahead:
					guest_welcome(reservation)
			except stripe.CardError, e:
				raise Reservation.ResActionError(e)
		else:
			raise Reservation.ResActionError("Unrecognized action.")

		messages.add_message(request, messages.INFO, 'Your action has been registered!')
		status_area_html = render(request, "snippets/res_status_area.html", {"r": reservation, 'location': location})
		return status_area_html

	except Reservation.ResActionError, e:
		messages.add_message(request, messages.INFO, "Error: %s" % e)
		return render(request, "snippets/res_status_area.html", {"r": reservation, 'location': location})

@house_admin_required
def ReservationChargeCard(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	#location = get_location(location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	try:
		reservation.charge_card()
		send_receipt(reservation)
		return HttpResponse()
	except stripe.CardError, e:
		return HttpResponse(status=500)

@house_admin_required
def ReservationSendReceipt(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_location(location_slug)
	reservation = Reservation.objects.get(id=reservation_id)
	if reservation.is_paid():
		send_receipt(reservation)
	messages.add_message(request, messages.INFO, "The receipt was sent.")
	return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))

@house_admin_required
def ReservationToggleComp(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_location(location_slug)
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
def ReservationSendMail(request, location_slug, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	location = get_location(location_slug)
	subject = request.POST.get("subject")
	recipient = [request.POST.get("recipient"),]
	body = request.POST.get("body") + "\n\n" + request.POST.get("footer")
	# TODO - This isn't fully implemented yet -JLS
	send_from_location_address(subject, body, None, recipient, location)

	reservation = Reservation.objects.get(id=reservation_id)
	reservation.mark_last_msg() 

	messages.add_message(request, messages.INFO, "Your message was sent.")
	return HttpResponseRedirect(reverse('reservation_manage', args=(location.slug, reservation_id)))

@house_admin_required
def payments_today(request, location_slug):
	today = timezone.localtime(timezone.now())
	return HttpResponseRedirect(reverse('core.views.payments', args=[], kwargs={'location_slug':location_slug, 'year':today.year, 'month':today.month}))

@house_admin_required
def payments(request, location_slug, year, month):
	location = get_location(location_slug)
	this_month = date(year=int(year), month=int(month), day=1)
	start = this_month - timedelta(days=1)
	day_next_month = this_month + timedelta(days=35)
	end = date(year=day_next_month.year, month=day_next_month.month, day=1)
	payments = Payment.objects.filter(reservation__location=location, payment_date__gt=start, payment_date__lt=end).order_by('payment_date').reverse()
	return render(request, "payments.html", {'payments': payments, 'location': location, 'this_month':this_month, 'previous_date':start, 'next_date':end })

# ******************************************************
#           registration callbacks and views
# ******************************************************


'''A registration backend that supports capturing user profile
information during registration.'''

	
class Registration(registration.views.RegistrationView):
	
	@transaction.commit_on_success
	def register(self, request, **cleaned_data):
		'''Register a new user, saving the User and UserProfile data.'''
		user = User()
		for field in user._meta.fields:
			if field.name in cleaned_data:
				setattr(user, field.name, cleaned_data[field.name])
		# the password has been validated by the form

		user.set_password(cleaned_data['password2'])
		user.save()

		profile = UserProfile(user=user)
		for field in profile._meta.fields:
			if field.name in cleaned_data:
				setattr(profile, field.name, cleaned_data[field.name])

		print "request data: image field"
		img_data = request.POST.get("image")
		# If none or len 0, means illegal image data
		if img_data == None or len(img_data) == 0:
			pass

		# Decode the image data
		img_data = base64.b64decode(img_data)
		filename = "%s.png" % uuid.uuid4()

		# XXX make the upload path a fixed setting in models, since it's
		# reference in three places
		upload_path = "data/avatars/%s/" % user.username
		upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
		if not os.path.exists(upload_abs_path):
			os.makedirs(upload_abs_path)
		full_file_name = os.path.join(upload_abs_path, filename)

		with open(full_file_name, 'wb') as f:
			f.write(img_data)
			f.close()

		profile.image = full_file_name
		profile.save()

		new_user = authenticate(username=user.username, password=cleaned_data['password2'])
		login(request, new_user)
		signals.user_activated.send(sender=self.__class__, user=new_user, request=request)
		return new_user

	def registration_allowed(self, request):
		if request.user.is_authenticated():
			return False
		else: return True

	def get_success_url(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		account activation. 

		We're not using the registration system's activation features ATM, so
		interrupt the registration process here.
		"""
		url_path = request.get_full_path().split("next=")
		if len(url_path) > 1 and url_path[1] == "/reservation/create/":
			messages.add_message(request, messages.INFO, 'Your account has been created. Now it is time to make a reservation!')
			return (url_path[1], (), {'username' : user.username})
		elif len(url_path) > 1 and url_path[1] == "/events/create/":
			messages.add_message(request, messages.INFO, 'Your account has been created. Now it is time to propose your event!')
			return (url_path[1], (), {'username' : user.username})
		else:
			return ('user_detail', (), {'username': user.username})

class Activation(registration.views.ActivationView):
	def activate(self, request, user):
		# we're not using the registration system's activation features ATM.
		return True




