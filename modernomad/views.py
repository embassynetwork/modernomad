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
	return render(request, "landing.html", {'coming_month': coming_month})

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
		if r.room.name == "Ada Lovelace Hostel":
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


def ReservationPayment(request):
	print request.POST
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	token = request.POST.get('stripeToken')
	save_card = request.POST.get('save-card')
	reservation_id = request.POST.get('res-id')
	amount_to_pay = request.POST.get('amount-paid')

	reservation = Reservation.objects.get(id=reservation_id)
	# account secret key 
	stripe.api_key = settings.STRIPE_SECRET_KEY

	saved_customer = True
	if not reservation.user.profile.customer_id:
		if save_card == "yes":
			customer = stripe.Customer.create(
					card=token,
					description=reservation.user.email
				)
			profile = reservation.user.profile
			profile.customer_id = customer.id
			profile.save()
		else:
			saved_customer = False
	
	domain = 'http://' + Site.objects.get_current().domain
	descr = "%s %s from %s - %s. Details: %s." % (reservation.user.first_name, 
			reservation.user.last_name, str(reservation.arrive), 
			str(reservation.depart), domain + reservation.get_absolute_url())

	if saved_customer:
		charge = stripe.Charge.create(
				amount=amount_to_pay, 
				currency="usd",
				customer = reservation.user.profile.customer_id,
				description=descr
		)
	else:
		# if the user didn't want to save their card, use the token directly to
		# create a one-time charge. 
		charge = stripe.Charge.create(
				amount=amount_to_pay,
				currency="usd",
				card=token,
				description=descr
		)

	print charge

	# set the status as paid and confirmed, and store the charge details
	reservation.status = Reservation.CONFIRMED
	reservation.save()
	reconcile = reservation.reconcile
	reconcile.status = Reconcile.PAID
	reconcile.payment_service = "Stripe"
	reconcile.payment_method = charge.card.type
	reconcile.paid_amount = (charge.amount/100)
	reconcile.transaction_id = charge.id
	reconcile.payment_date = datetime.datetime.now()
	reconcile.save()

	reservation.reconcile.send_receipt()
	variables = {
		'first_name': reservation.user.first_name, 
		'last_name': reservation.user.last_name, 
		'res_id': reservation.id,
		'today': datetime.datetime.today(), 
		'arrive': reservation.arrive, 
		'depart': reservation.depart, 
		'room': reservation.room.name, 
		'num_nights': reservation.total_nights(), 
		'rate': reservation.reconcile.get_rate(), 
		'payment_method': reservation.reconcile.payment_method,
		'transaction_id': reservation.reconcile.transaction_id,
		'payment_date': reservation.reconcile.payment_date,
		'total_paid': reservation.reconcile.paid_amount
	}

	messages.add_message(request, messages.INFO, 'Thank you! This receipt has been emailed to you at %s.' % reservation.user.email)
	return render(request, "showreceipt.html", variables)


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

