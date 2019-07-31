import datetime
import logging
import json
from json import JSONEncoder

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import TemplateView
try:
    from django.template import get_template
except ImportError:
    from django.template.loader import get_template

from django.utils import timezone
import maya
from rest_framework import mixins
from rest_framework import generics

from .view_helpers import _get_user_and_perms
from modernomad.core.emails.messages import send_booking_receipt, new_booking_notify
from modernomad.core.forms import BookingUseForm
from modernomad.core.models import Booking, Use, Location, Resource, Fee
from modernomad.core.shortcuts import get_qs_or_404
from modernomad.core.serializers import ResourceSerializer, FeeSerializer

ensure_csrf = method_decorator(ensure_csrf_cookie)
logger = logging.getLogger(__name__)


class DateEncoder(JSONEncoder):
    def default(self, o):
        try:
            return o.strftime(settings.DATE_FORMAT)
        except Exception:
            return super().default(o)


class RoomApiList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    lookup_field = 'location_slug'

    def filter_queryset(self, queryset):
        # TODO make sure that capacity_change and uses are prefetched somehow
        # ideally a method on Resource manager

        def room_available_during_period(room, arrive, depart):
            availabilities = room.daily_availabilities_within(arrive, depart)
            zero_quantity_dates = [avail for avail in availabilities if avail[1] == 0]
            if zero_quantity_dates:
                return False
            return True

        qs = queryset.filter(location__slug=self.kwargs['location_slug'])
        params = self.request.query_params.dict()
        if params:
            arrive = maya.parse(params['arrive']).date
            depart = maya.parse(params['depart']).date

            room_ids = [
                room.pk for room in qs
                if room_available_during_period(room, arrive, depart)
            ]
            qs = qs.filter(id__in=room_ids)
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RoomApiDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    lookup_url_kwarg = 'room_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class StayView(TemplateView):
    # This view should be moved to views/location.py which is up for a PR.
    template_name = 'booking/booking.html'

    @ensure_csrf
    def get(self, request, *args, **kwargs):
        room_id = kwargs.get('room_id')
        if room_id:
            self.room = get_qs_or_404(Resource, pk=room_id).select_related('location').first()
            self.location = self.room.location
        else:
            self.room = None
            self.location = get_object_or_404(Location, slug=kwargs.get('location_slug'))

        if not self.location.rooms_with_future_capacity():
            msg = 'Sorry! This location does not currently have any listings.'
            messages.add_message(self.request, messages.INFO, msg)
            return HttpResponseRedirect(reverse("location_detail", args=(self.location.slug, )))

        return super().get(request, *args, **kwargs)

    def populate_room(self, context, resource_data, many):
        resource = ResourceSerializer(
            resource_data, many=many, context={'request': self.request}
        )

        if many:
            context['rooms'] = resource.data
        else:
            context['room'] = resource.data
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = self.location

        is_admin = self.location.house_admins.all().filter(pk=self.request.user.pk).exists()
        if self.request.user.is_authenticated():
            user_drft_balance = self.request.user.profile.drft_spending_balance()
        else:
            user_drft_balance = 0
        
        fees = Fee.objects.filter(locationfee__location=self.location)

        react_data = {
            'is_house_admin': is_admin,
            'user_drft_balance': user_drft_balance,
            'fees': FeeSerializer(fees, many=True).data
        }

        resource_data = self.room if self.room else self.location.rooms_with_future_capacity()
        use_many = False if self.room else True
        react_data = self.populate_room(react_data, resource_data, use_many)

        context['react_data'] = json.dumps(react_data, cls=DateEncoder)
        return context


def BookingSubmit(request, location_slug):
    if not request.method == "POST":
        return HttpResponseRedirect("/404")

    location = get_object_or_404(Location, slug=location_slug)

    form = BookingUseForm(location, request.POST)
    if form.is_valid():
        comments = request.POST.get('comments')
        use = form.save(commit=False)
        use.location = location
        booking = Booking(use=use, comments=comments)
        # reset_rate also generates the bill.
        if request.user.is_authenticated():
            use.user = request.user
            if use.suggest_drft():
                use.accounted_by = Use.DRFT
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
        logger.debug('form was not valid')
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
        use = booking.use
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
        if use.arrive >= datetime.date.today():
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
        uses = Use.objects.filter(status="confirmed").filter(location=location).exclude(depart__lt=use.arrive).exclude(arrive__gt=use.depart)
        for use in uses:
            if use.user not in users_during_stay:
                users_during_stay.append(use.user)
        for member in location.residents():
            if member not in users_during_stay:
                users_during_stay.append(member)

        user_drft_balance = request.user.profile.drft_spending_balance()

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
    c = {
        'today': timezone.localtime(timezone.now()),
        'user': booking.use.user,
        'location': booking.use.location,
        'booking': booking,
        'booking_url': "https://" + Site.objects.get_current().domain + booking.get_absolute_url()
    }
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
                logger.debug('comments?')
                logger.debug(comments)
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
        except stripe.CardError as e:
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
