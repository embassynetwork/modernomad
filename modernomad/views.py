from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from core.models import Reservation, UserProfile, Reconcile
from gather.models import Event
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from core.confirmation_email import confirmation_email_details
import json, datetime, stripe 
from django.conf import settings
from core.forms import PaymentForm
from reservation_calendar import GuestCalendar
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.contrib.sites.models import Site
from django.contrib import messages
import eventbrite
from gather.tasks import published_events_today_local, events_pending


def index(request):
	today = datetime.date.today()
	
	# pull out all reservations in the coming month
	coming_month_res = (
			Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
			.exclude(depart__lt=today)
			.exclude( arrive__gt=today+datetime.timedelta(days=30))
		)

	coming_month_events = (
			Event.objects.filter(status="live") 
			.exclude(end__lt=today)
			.exclude( start__gte=today+datetime.timedelta(days=30))
		)

	# add users associated with those reservations and events to a list to display on
	# the homepage
	coming_month = []
	for r in coming_month_res:
		# check for duplicates, add if not already there.
		if r.user not in coming_month:
			coming_month.append(r.user)

	for e in coming_month_events:
		# check for duplicates, add if not already there.
		for u in e.organizers.all():
			if u not in coming_month:
				coming_month.append(u)
	
	residents = User.objects.filter(groups__name='residents')
	residents = list(residents)

	# add residents to the list of people in the house in the coming month. 
	for r in residents:
		# check for duplicates, add if not already there.
		if r not in coming_month:
			coming_month.append(r)

	if request.user.is_authenticated():
		current_user = request.user
	else:
		current_user = None
	events = Event.objects.upcoming(upto=5, current_user=current_user)

	return render(request, "landing.html", {'coming_month': coming_month, 'events': events})

def about(request):
	return render(request, "about.html")

def coworking(request):
	return render(request, "coworking.html")

def residents(request):
	residents = User.objects.filter(groups__name='residents')
	return render(request, "residents.html", {'residents': residents})


def projects(request):
	#residents = User.objects.filter(groups__name='residents')
	#return render(request, "community.html", {'people': residents})
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

def today(request):
	# get all the reservations that intersect today (including those departing
	# and arriving today)
	today = timezone.now()
	reservations_today = Reservation.objects.filter(Q(status="confirmed") | Q(status="approved")).exclude(depart__lt=today).exclude(arrive__gt=today)
	guests_today = []
	for r in reservations_today:
		guests_today.append(r.user)
	residents = User.objects.filter(groups__name='residents')
	people_today = guests_today + list(residents)

	events_today = published_events_today_local()
	return render(request, "today.html", {'people_today': people_today, 'events_today': events_today})


def occupancy(request):
	if not (request.user.is_authenticated and request.user.groups.filter(name='house_admin')):
		return HttpResponseRedirect(("/404"))
	today = datetime.date.today()
	month = request.GET.get("month")
	year = request.GET.get("year")

	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)

	# note the day parameter is meaningless
	report_date = datetime.date(year, month, 1) 
	reservations = Reservation.objects.filter(status="confirmed").exclude(depart__lt=start).exclude(arrive__gt=end)

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

	reconciles_this_month = Reconcile.objects.filter(payment_date__gte=start).filter(payment_date__lte=end).filter(status="paid")
	for r in reconciles_this_month:
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
		
		elif r.reservation.arrive >= start and r.reservation.depart > end:
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
		rate = r.reconcile.get_rate()
		if r.reconcile.status == Reconcile.COMP:
			total_comped_nights += nights_this_month
			total_comped_income += nights_this_month*r.reconcile.default_rate()
			comp = True
			unpaid = False
		else:
			total_income += nights_this_month*rate
			this_room_income = room_income.get(r.room.name, 0)
			this_room_income += rate*nights_this_month
			room_income[r.room.name] = this_room_income

			if r.reconcile.status == Reconcile.PAID:
				if r.reconcile.payment_date < start:
					income_from_past_months += nights_this_month*(r.reconcile.paid_amount/(r.depart - r.arrive).days)
				else:
					income_for_this_month += nights_this_month*(r.reconcile.paid_amount/(r.depart - r.arrive).days) 

			if r.reconcile.status == Reconcile.UNPAID or r.reconcile.status == Reconcile.INVOICED:
				unpaid = True
				unpaid_total += nights_this_month*rate
			else:
				unpaid = False

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
			if r.reconcile.status != Reconcile.COMP:
				total_income_shared += nights_this_month*rate
		else:
			total_private_nights += nights_this_month
			if r.reconcile.status != Reconcile.COMP:
				total_income_private += nights_this_month*rate

	print room_income

	return render(request, "occupancy.html", {"data": person_nights_data, 
		'total_nights':total_person_nights, 'total_income':total_income, 'unpaid_total': unpaid_total,
		'total_shared_nights': total_shared_nights, 'total_private_nights': total_private_nights,
		'total_comped_income': total_comped_income, 'total_comped_nights': total_comped_nights,
		"next_month": next_month, "prev_month": prev_month, "total_income_shared": total_income_shared,
		"total_income_private": total_income_private, "report_date": report_date, 'room_income':room_income, 
		'income_for_this_month': income_for_this_month, 'income_for_future_months':income_for_future_months, 
		'income_from_past_months': income_from_past_months, 'income_for_past_months':income_for_past_months })

@login_required
def calendar(request):
	today = datetime.date.today()
	month = request.GET.get("month")
	year = request.GET.get("year")

	start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
	report_date = datetime.date(year, month, 1) 

	reservations = Reservation.objects.filter(Q(status="confirmed") | Q(status="approved")).exclude(depart__lt=start).exclude(arrive__gt=end).order_by('arrive')
	
	# create the calendar object
	guest_calendar = GuestCalendar(reservations, year, month).formatmonth(year, month)

	return render(request, "calendar.html", {'reservations': reservations, 
		'calendar': mark_safe(guest_calendar), "next_month": next_month, 
		"prev_month": prev_month, "report_date": report_date })

def stay(request):
	return render(request, "stay.html")


def GenericPayment(request):
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

def ErrorView(request):
	return render(request, '404.html')

@login_required
def GuestInfo(request):
	# only allow people who have had at least one confirmed reservation access this page
	confirmed = Reservation.objects.filter(user=request.user).filter(status='confirmed')
	if len(confirmed) > 0:
		return render(request, 'guestinfo.html', {'static_info': confirmation_email_details})
	return HttpResponseRedirect('/')

