from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Reservation, UserProfile, Reconcile
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


def new_home(request):
	today = datetime.date.today()
	coming_month_res = (
			Reservation.objects.filter(Q(status="confirmed") | Q(status="approved"))
			.exclude(depart__lt=today)
			.exclude( arrive__gt=today+datetime.timedelta(days=30))
		)
	coming_month = []
	for r in coming_month_res:
		coming_month.append(r.user)
	residents = User.objects.filter(groups__name='residents')
	coming_month += list(residents)

	# get any events
	eb_auth_tokens = {
			'app_key':  settings.EVENTBRITE_APP_KEY, 
			'user_key': settings.EVENTBRITE_USER_KEY
		}
	eb_client = eventbrite.EventbriteClient(eb_auth_tokens)
	response = eb_client.user_list_events()
	events = response['events']
	return render(request, "landing.html", {'coming_month': coming_month, 'events': events})

def index(request):
	return render(request, "index.html")
	
def about(request):
	return render(request, "about.html")

def community(request):
	residents = User.objects.filter(groups__name='residents')
	return render(request, "community.html", {'people': residents})

def events(request):
	return render(request, "events.html")

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
	today = datetime.date.today()
	reservations_today = Reservation.objects.filter(Q(status="confirmed") | Q(status="approved")).exclude(depart__lt=today).exclude(arrive__gt=today)
	guests_today = []
	for r in reservations_today:
		guests_today.append(r.user)
	residents = User.objects.filter(groups__name='residents')
	people_today = guests_today + list(residents)
	return render(request, "today.html", {'people_today': people_today})


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

	return render(request, "occupancy.html", {"data": person_nights_data, 
		'total_nights':total_person_nights, 'total_income':total_income, 'unpaid_total': unpaid_total,
		'total_shared_nights': total_shared_nights, 'total_private_nights': total_private_nights,
		'total_comped_income': total_comped_income, 'total_comped_nights': total_comped_nights,
		"next_month": next_month, "prev_month": prev_month, "total_income_shared": total_income_shared,
		"total_income_private": total_income_private, "report_date": report_date})

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

def participate(request):
	return render(request, "participate.html")



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

