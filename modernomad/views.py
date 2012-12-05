from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Reservation
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from core.confirmation_email import confirmation_email_details
from core.models import Reservation
import json, datetime, stripe 
import settings
from core.forms import PaymentForm

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

def contribute(request):
	if request.method == 'POST':
		form = PaymentForm(request.POST)
		if form.is_valid():
			# account secret key (NOTE: THIS IS A TEST KEY)
			stripe.api_key = settings.STRIPE_SECRET_KEY
			
			# get the payment details from the form
			token = request.POST.get('stripeToken')
			charge_amt = int(request.POST.get('amount'))
			pay_name = request.POST.get('name')
			pay_email = request.POST.get('email')
			comment  = request.POST.get('comment')

		    # create the charge on Stripe's servers - this will charge the user's card
			charge = stripe.Charge.create(
					amount=charge_amt*100, # convert dollars to cents
					currency="usd",
					card=token,
					description= "from %s: %s" % (pay_email, comment)
			)

			# TODO error handling if charge does not succeed
			return HttpResponseRedirect("/thanks")
	else:
		form = PaymentForm()		
	return render(request, "contribute.html", {'form': form})

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

