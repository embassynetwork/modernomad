from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core import urlresolvers
from models import Reservation, Payment
from django.conf import settings
from django.utils import timezone
import stripe

import logging

logger = logging.getLogger(__name__)

class PaymentException(Exception):
	pass

def charge_card(reservation):
	if settings.STRIPE_SECRET_KEY:
		return stripe_charge_card(reservation)
	elif settings.USA_E_PAY_KEY:
		return usaepay_charge_card(reservation)
	else:
		raise PaymentException("No payment system configured")

def issue_refund(payment):
	if settings.STRIPE_SECRET_KEY:
		return stripe_issue_refund(payment)
	elif settings.USA_E_PAY_KEY:
		return usaepay_issue_refund(payment)
	else:
		raise PaymentException("No payment system configured")

###################################################################
# Stripe Methods
###################################################################

def stripe_charge_card(reservation):
	logger.debug("stripe_charge_card(reservation=%s)" + str(reservation.id))
	
	# stripe will raise a stripe.CardError if the charge fails. this
	# function purposefully does not handle that error so the calling
	# function can decide what to do.
	reservation_url = "https://" + Site.objects.get_current().domain + urlresolvers.reverse('reservation_detail', args=(reservation.location.slug, reservation.id))
	descr = "%s from %s - %s. Details: %s." % (reservation.user.get_full_name(),
			str(reservation.arrive), str(reservation.depart), reservation_url)

	amt_owed = reservation.total_owed()
	amt_owed_cents = int(amt_owed * 100)
	stripe.api_key = settings.STRIPE_SECRET_KEY
	charge = stripe.Charge.create(
			amount=amt_owed_cents,
			currency="usd",
			customer = reservation.user.profile.customer_id,
			description=descr
			)

	# Store the charge details in a Payment object
	return Payment.objects.create(reservation=reservation,
		payment_service = "Stripe",
		payment_method = "Credit Card",
		paid_amount = (amt_owed),
		transaction_id = charge.id
	)

def stripe_issue_refund(payment):
	# https://stripe.com/docs/api#create_refund
	logger.debug("stripe_issue_refund(payment=%s)" + payment.id)
	return None
	
###################################################################
# USAePay Methods
###################################################################

def usaepay_charge_card(reservation):
	logger.debug("usaepay_charge_card(reservation=%s)" + str(reservation.id))
	return None

def usaepay_issue_refund(payment):
	logger.debug("usaepay_issue_refund(payment=%s)" + payment.id)
	return None
