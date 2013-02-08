from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Reservation, UserProfile
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from core.confirmation_email import confirmation_email_details
from core.models import Reservation
import json, datetime, stripe 
import settings
from core.forms import PaymentForm

def landing(request):
	return render(request, "landing.html")
	
def home(request):
	return render(request, "home.html")

def about(request):
	return render(request, "about.html")

def community(request):
	residents = User.objects.filter(groups__name='residents')
	print len(residents)
	return render(request, "community.html", {'people': residents})

def events(request):
	return render(request, "events.html")

def upcomingTimeline(request):
	return render(request, "upcoming-timeline.html")

@login_required
def upcoming(request):
	today = datetime.date.today()
	upcoming = Reservation.objects.filter(status="confirmed").order_by('arrive').exclude(arrive__lt=today)
	arrived = Reservation.objects.filter(status="confirmed").order_by('arrive').exclude(depart__lt=today).exclude(arrive__gte=today)
	return render(request, "upcoming.html", {'upcoming': upcoming, 'arrived': arrived, 'today': today})

def stay(request):
	return render(request, "stay.html")

def participate(request):
	return render(request, "participate.html")

def payment(request):
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
			if comment:
				charge_descr = "from %s: %s" % (pay_email, comment)
			else:
				charge_descr = ""
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

