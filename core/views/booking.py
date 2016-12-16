from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .view_helpers import _get_user_and_perms
import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
import logging
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from core.emails import send_booking_receipt, new_booking_notify
from django.views.decorators.csrf import ensure_csrf_cookie

from core.models import Booking, Use, Location, Site
from core.forms import BookingUseForm
from bank.models import Currency, Account


logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def StayComponent(request, location_slug, room_id=None):
    user_drft_balance = Account.objects.user_balance(currency=Currency.objects.get(name='DRFT'), user=request.user)


    return render(request,
        'booking.html',
        {
            "request_user_drft_balance": user_drft_balance
        })


def BookingSubmit(request, location_slug):
    if not request.method == "POST":
        return HttpResponseRedirect("/404")

    location = get_object_or_404(Location, slug=location_slug)

    form = BookingUseForm(location, request.POST)
    if form.is_valid():
        print 'form is valid'
        comments = request.POST.get('comments')
        use = form.save(commit=False)
        use.location = location
        booking = Booking(use=use, comments=comments)
        # reset_rate also generates the bill.
        if request.user.is_authenticated():
            use.user = request.user
            use.save()
            # we already set the value of 'use' when creating the Booking,
            # but it wasn't saved at that point, and Django complains about
            # a missing primary key here otherwise, so re-setting.
            booking.use = use
            booking.save()
            booking.reset_rate()
            new_booking_notify(booking)
            messages.add_message(
                request,
                messages.INFO,
                'Thanks! Your booking was submitted. You will receive an email when it has been reviewed. You may wish to <a href="/people/%s/edit/">update your profile</a> if your projects or ideas have changed since your last visit.' % booking.use.user.username
            )
            return HttpResponseRedirect(reverse('booking_detail', args=(location_slug, booking.id)))
        else:
            booking_data = booking.serialize()
            request.session['booking'] = booking_data
            messages.add_message(request, messages.INFO, 'Thank you! Please make a profile to complete your booking request.')
            return HttpResponseRedirect(reverse('registration_register'))
    else:
        print 'form was not valid'
        logger.debug(request.POST)
        logger.debug(form.errors)
        raise Exception(str(form.errors.as_data()))

    # pass the rate for each room to the template so we can update the cost of
    # a booking in real time.
    # today = timezone.localtime(timezone.now())
    # month = request.GET.get("month")
    # year = request.GET.get("year")
    # start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
    # rooms = location.rooms_with_future_capacity()
    # return render(
    #     request,
    #     'booking.html',
    #     {}
    # )


@login_required
def UserBookings(request, username):
    ''' TODO: rethink permissions here'''
    user, user_is_house_admin_somewhere = _get_user_and_perms(request, username)
    # uses = Use.objects.filter(user=user).exclude(status='deleted').order_by('arrive')
    bookings = Booking.objects.filter(use__user=user).exclude(use__status='deleted')
    past_bookings = []
    upcoming_bookings = []
    for booking in bookings:
        if booking.use.arrive >= datetime.date.today():
            upcoming_bookings.append(booking)
        else:
            past_bookings.append(booking)

    return render(
        request,
        "user_bookings.html",
        {
            "u": user,
            'user_is_house_admin_somewhere': user_is_house_admin_somewhere,
            'past_bookings': past_bookings,
            'upcoming_bookings': upcoming_bookings,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    )


@login_required
def BookingDetail(request, booking_id, location_slug):
    location = get_object_or_404(Location, slug=location_slug)
    try:
        booking = Booking.objects.get(id=booking_id)
        if not booking:
            raise Booking.DoesNotExist
    except Booking.DoesNotExist:
        msg = 'The booking you requested do not exist'
        messages.add_message(request, messages.ERROR, msg)
        return HttpResponseRedirect('/404')
    # make sure the user is either an admin, resident or the booking holder
    # (we can't use the decorator here because the user themselves also has to
    # be able to see the page).
    if ((request.user == booking.use.user) or
            (request.user in location.house_admins.all()) or
            (request.user in location.readonly_admins.all()) or
            (request.user in location.residents.all())):
        if booking.use.arrive >= datetime.date.today():
            past = False
        else:
            past = True
        if booking.is_paid():
            paid = True
        else:
            paid = False

        domain = Site.objects.get_current().domain

        # users that intersect this stay
        users_during_stay = []
        uses = Use.objects.filter(status="confirmed").filter(location=location).exclude(depart__lt=booking.use.arrive).exclude(arrive__gt=booking.use.depart)
        for use in uses:
            if use.user not in users_during_stay:
                users_during_stay.append(use.user)
        for member in location.residents():
            if member not in users_during_stay:
                users_during_stay.append(member)

        room_accepts_drft = False
        drft_balance = 0

        # try
        user_drft_balance = Account.objects.user_balance(currency=Currency.objects.get(name='DRFT'), user=request.user)


        if booking.use.resource.backing and booking.use.resource.backing.accepts_drft:
            room_accepts_drft = True
        # except:
            # continues silently if no DRFT and room backing have not been
            # setup.
        #    pass



        return render(
            request,
            "booking_detail.html",
            {
                "booking": booking,
                "past": past,
                'location': location,
                "domain": domain,
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                "paid": paid,
                "contact": location.from_email(),
                'users_during_stay': users_during_stay,
                'drft_balance': user_drft_balance,
                'room_accepts_drft': room_accepts_drft,
            }
        )
    else:
        messages.add_message(request, messages.INFO, "You do not have permission to view that booking")
        return HttpResponseRedirect('/404')


@login_required
def BookingReceipt(request, location_slug, booking_id):
    location = get_object_or_404(Location, slug=location_slug)
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.use.user or location != booking.use.location:
        if not request.user.is_staff:
            return HttpResponseRedirect("/404")

    # I want to render the receipt exactly like we do in the email
    htmltext = get_template('emails/receipt.html')
    c = Context({
        'today': timezone.localtime(timezone.now()),
        'user': booking.use.user,
        'location': booking.use.location,
        'booking': booking,
        'booking_url': "https://" + Site.objects.get_current().domain + booking.get_absolute_url()
        })
    receipt_html = htmltext.render(c)

    return render(
        request,
        'booking_receipt.html',
        {
            'receipt_html': receipt_html,
            'booking': booking,
            'location': location
        }
    )


@login_required
def BookingEdit(request, booking_id, location_slug):
    logger.debug("Entering BookingEdit")

    location = get_object_or_404(Location, slug=location_slug)
    booking = Booking.objects.get(id=booking_id)
    # need to pull these dates out before we pass the instance into
    # the BookingUseForm, since it (apparently) updates the instance
    # immediately (which is weird, since it hasn't validated the form
    # yet!)
    original_arrive = booking.use.arrive
    original_depart = booking.use.depart
    original_room = booking.use.resource
    if request.user.is_authenticated() and request.user == booking.use.user:
        logger.debug("BookingEdit: Authenticated and same user")
        if request.user in booking.use.location.house_admins.all():
            is_house_admin = True
        else:
            is_house_admin = False

        if request.method == "POST":
            logger.debug("BookingEdit: POST")
            form = BookingUseForm(location, request.POST, instance=booking.use)
            if form.is_valid():
                logger.debug("BookingEdit: Valid Form")
                comments = request.POST.get('comments')
                print 'comments?'
                print comments
                booking.comments = comments
                booking.generate_bill()
                booking.save()
                form.save()
                if (
                    not booking.is_pending() and
                    (
                        booking.use.arrive != original_arrive or
                        booking.use.depart != original_depart or
                        booking.use.resource != original_room
                    )
                ):
                    logger.debug("booking room or date was changed. updating status.")
                    booking.pending()
                    # notify house_admins by email
                    try:
                        updated_booking_notify(booking)
                    except:
                        logger.debug("Booking %d was updated but admin notification failed to send" % booking.id)
                    client_msg = 'The booking was updated and the new information will be reviewed for availability.'
                else:
                    client_msg = 'The booking was updated.'
                # save the instance *after* the status has been updated as needed.
                messages.add_message(request, messages.INFO, client_msg)
                return HttpResponseRedirect(reverse("booking_detail", args=(location.slug, booking_id)))
        else:
            # form = get_booking_form_for_perms(request, post=False, instance=booking)
            form = BookingUseForm(location, instance=booking.use)

        return render(
            request,
            'booking_edit.html',
            {
                'form': form,
                'booking_id': booking_id,
                'arrive': booking.use.arrive,
                'depart': booking.use.depart,
                'is_house_admin': is_house_admin,
                'max_days': location.max_booking_days,
                'location': location
            }
        )
    else:
        return HttpResponseRedirect("/")


@login_required
def BookingConfirm(request, booking_id, location_slug):
    booking = Booking.objects.get(id=booking_id)
    if not (
        request.user.is_authenticated() and
        request.user == booking.use.user and
        request.method == "POST" and
        booking.is_approved()
    ):
        return HttpResponseRedirect("/")

    if not booking.use.user.profile.customer_id:
        messages.add_message(request, messages.INFO, 'Please enter payment information to confirm your booking.')
    else:
        try:
            payment_gateway.charge_booking(booking)
            booking.confirm()
            send_booking_receipt(booking)
            # if booking start date is sooner than WELCOME_EMAIL_DAYS_AHEAD,
            # need to send them house info manually.
            days_until_arrival = (booking.arrive - datetime.date.today()).days
            if days_until_arrival <= booking.use.location.welcome_email_days_ahead:
                guest_welcome(booking)

            messages.add_message(
                request,
                messages.INFO,
                'Thank you! Your payment has been received and a receipt emailed to you at %s' % booking.use.user.email)
        except stripe.CardError, e:
            messages.add_message(
                request,
                messages.WARNING,
                'Drat, it looks like there was a problem with your card: %s. Please add a different card on your ' +
                '<a href="/people/%s/edit/">profile</a>.' % (booking.use.user.username, e)
            )

    return HttpResponseRedirect(reverse('booking_detail', args=(location_slug, booking.id)))


@login_required
def BookingDelete(request, booking_id, location_slug):
    booking = Booking.objects.get(id=booking_id)
    if (
        request.user.is_authenticated() and
        request.user == booking.use.user and
        request.method == "POST"
    ):
        booking.cancel()

        messages.add_message(request, messages.INFO, 'Your booking has been cancelled.')
        username = booking.use.user.username
        return HttpResponseRedirect("/people/%s" % username)

    else:
        return HttpResponseRedirect("/")

    html += "</div>"
    return HttpResponse(html)


@login_required
def BookingCancel(request, booking_id, location_slug):
    if not request.method == "POST":
        return HttpResponseRedirect("/404")

    location = get_object_or_404(Location, slug=location_slug)
    booking = Booking.objects.get(id=booking_id)
    if (
        not (
            request.user.is_authenticated() and
            request.user == booking.use.user
        ) and
        request.user not in location.house_admins.all()
    ):
        return HttpResponseRedirect("/404")

    redirect = request.POST.get("redirect")

    booking.cancel()
    messages.add_message(request, messages.INFO, 'The booking has been cancelled.')
    username = booking.use.user.username
    return HttpResponseRedirect(redirect)
