from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core import urlresolvers
from modernomad.core.models import Booking, Payment
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import stripe

import logging

logger = logging.getLogger(__name__)

class PaymentException(Exception):
    pass

def charge_booking(booking):
    if settings.STRIPE_SECRET_KEY:
        return stripe_charge_booking(booking)
    elif settings.USA_E_PAY_KEY:
        return usaepay_charge_booking(booking)
    else:
        raise PaymentException("No payment system configured")

def charge_user(user, bill, amount, reference):
    if settings.STRIPE_SECRET_KEY:
        return stripe_charge_user(user, bill, amount, reference)
    else:
        raise PaymentException("Payment system not configured")

def issue_refund(payment, amount=None):
    if payment.payment_service == "Stripe" and settings.STRIPE_SECRET_KEY:
        return stripe_issue_refund(payment, amount)
    elif payment.payment_service == "USAePay" and settings.USA_E_PAY_KEY:
        return usaepay_issue_refund(payment, amount)
    elif not payment.payment_service == "Stripe" and not payment.payment_service == "USAePay":
        logger.info("issue_refund: Payment not issued through service so we can't refund it.")
        return Payment.objects.create(bill=payment.bill,
            user = payment.user,
            payment_service = payment.payment_service,
            paid_amount = -1 * payment.paid_amount,
            payment_method = "Refund",
            transaction_id = "Manual",
        )
    else:
        raise PaymentException("No payment system configured")

###################################################################
# Stripe Methods
###################################################################

def charge_description(booking):
    booking_url = "https://" + Site.objects.get_current().domain + urlresolvers.reverse('booking_detail', args=(booking.use.location.slug, booking.id))
    descr = "%s from %s - %s. Details: %s." % (booking.use.user.get_full_name(),
            str(booking.use.arrive), str(booking.use.depart), booking_url)
    return descr


def stripe_charge_card_third_party(booking, amount, token, charge_descr):
    logger.debug("stripe_charge_card_third_party(booking=%s)" % booking.id)
    logger.debug('in charge card 3rd party')

    # stripe will raise a stripe.CardError if the charge fails. this
    # function purposefully does not handle that error so the calling
    # function can decide what to do.
    descr = charge_description(booking)
    descr += charge_descr

    amt_owed_cents = int(amount * 100)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    charge = stripe.Charge.create(
            amount=amt_owed_cents,
            currency="usd",
            card=token,
            description= descr
    )
    return charge

def stripe_charge_user(user, bill, amount_dollars, reference):
    logger.debug("stripe_charge_user(%s, %s, %d, %s)" % (user, bill, amount_dollars, reference))

    # stripe will raise a stripe.CardError if the charge fails. this
    # function purposefully does not handle that error so the calling
    # function can decide what to do.

    amt_cents = int(amount_dollars * 100)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    charge = stripe.Charge.create(
            amount=amt_cents,
            currency="usd",
            customer = user.profile.customer_id,
            description= reference
        )

    # Store the charge details in a Payment object
    return Payment.objects.create(bill=bill,
        user = user,
        payment_service = "Stripe",
        payment_method = charge.source.brand,
        paid_amount = amount_dollars,
        transaction_id = charge.id,
        last4 = charge.source.last4
    )

def stripe_charge_booking(booking):
    logger.debug("stripe_charge_booking(booking=%s)" % booking.id)

    # stripe will raise a stripe.CardError if the charge fails. this
    # function purposefully does not handle that error so the calling
    # function can decide what to do.
    descr = charge_description(booking)

    amt_owed = booking.bill.total_owed()
    amt_owed_cents = int(amt_owed * 100)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    charge = stripe.Charge.create(
            amount=amt_owed_cents,
            currency="usd",
            customer = booking.use.user.profile.customer_id,
            description=descr
        )

    # Store the charge details in a Payment object
    return Payment.objects.create(bill=booking.bill,
        user = booking.use.user,
        payment_service = "Stripe",
        payment_method = charge.source.brand,
        paid_amount = amt_owed,
        transaction_id = charge.id,
        last4 = charge.source.last4
    )

def stripe_issue_refund(payment, refund_amount=None):
    logger.debug("stripe_issue_refund(payment=%s)" % payment.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    charge = stripe.Charge.retrieve(payment.transaction_id)
    logger.debug("refunding amount")
    logger.debug(refund_amount)
    if refund_amount:
        # amount refunded has to be given in cents
        refund_amount_cents = int(float(refund_amount)*100)
        logger.debug(refund_amount_cents)
        refund = charge.refund(amount=refund_amount_cents)
    else:
        refund = charge.refund()

    # Store the charge details in a Payment object
    return Payment.objects.create(bill=payment.bill,
        user = payment.user,
        payment_service = "Stripe",
        payment_method = "Refund",
        paid_amount = -1 * Decimal(refund_amount),
        transaction_id = refund.id
    )

###################################################################
# USAePay Methods
###################################################################

def usaepay_charge_booking(booking):
    logger.debug("usaepay_charge_card(booking=%s)" % booking.id)
    return None

def usaepay_issue_refund(payment):
    logger.debug("usaepay_issue_refund(payment=%s)" % payment.id)
    return None
