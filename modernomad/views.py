from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Reservation
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from core.confirmation_email import confirmation_email_details
from core.models import Reservation
import json, datetime

def index(request):
	return render(request, "index.html")
	
def about(request):
	return render(request, "about.html")

def residents(request):
	return render(request, "residents.html")

def events(request):
	return render(request, "events.html")

def upcomingTimeline(request):
	return render(request, "upcoming-timeline.html")

def upcoming(request):
	# method formats the upcoming reservations as JSON appropriate 
	# for consumption by the timelineJS library. 

	today = datetime.date.today()
	upcoming = Reservation.objects.order_by('arrive').exclude(arrive__lt=today)
	arrived = Reservation.objects.order_by('arrive').exclude(depart__lt=today).exclude(arrive__gte=today)
	return render(request, "upcoming.html", {'upcoming': upcoming, 'arrived': arrived, 'today': today})

def stay(request):
	return render(request, "stay.html")

def payment(request):
	return render(request, "payment.html")

def submitpayment(request):
	if request.method != "POST":
		return render(request, "index.html")

	# account secret key (NOTE: THIS IS A TEST KEY)
	stripe.api_key = "sk_0DkOebiI0BuKUOxg9KVcRRfMQT8FJ"
	
	# get the payment details from the form
	token = request.POST['stripeToken']
	charge_amt = request.POST['card-amount']
	pay_name = request.POST['human-name']
	pay_email = request.POST['human-email']

    # create the charge on Stripe's servers - this will charge the user's card
	charge = stripe.Charge.create(
			amount=charge_amt*100, # convert dollars to cents
			currency="usd",
			card=token,
			description=human_email
	)

	return render(request, "stay.html")

def ErrorView(request):
	return render(request, '404.html')

@login_required
def GuestInfo(request):
	# only allow people who have had at least one confirmed reservation access this page
	confirmed = Reservation.objects.filter(user=request.user).filter(status='confirmed')
	if len(confirmed) > 0:
		return render(request, 'guestinfo.html', {'static_info': confirmation_email_details})
	return HttpResponseRedirect('/')

