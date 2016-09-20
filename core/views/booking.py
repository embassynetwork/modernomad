from django.shortcuts import get_object_or_404
from core.models import *
from core.forms import ReservationForm
from django.utils import timezone
from core.views.unsorted import get_calendar_dates
from django.shortcuts import render

def ReservationSubmit(request, location_slug):
    location = get_object_or_404(Location, slug=location_slug)
    if request.method == 'POST':
        form = ReservationForm(location, request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.location = location
            if request.user.is_authenticated():
                reservation.user = request.user
                reservation.save()
                # Make sure the rate is set and then generate a bill
                reservation.reset_rate()
                new_reservation_notify(reservation)
                messages.add_message(
                    request,
                    messages.INFO,
                    'Thanks! Your reservation was submitted. You will receive an email when it has been reviewed. You may wish to <a href="/people/%s/edit/">update your profile</a> if your projects or ideas have changed since your last visit.' % reservation.user.username
                )
                return HttpResponseRedirect(reverse('reservation_detail', args=(location_slug, reservation.id)))
            else:
                res_info = reservation.serialize()
                request.session['reservation'] = res_info
                messages.add_message(request, messages.INFO, 'Thank you! Please make a profile to complete your reservation request.')
                return HttpResponseRedirect(reverse('registration_register'))
        else:
            logger.debug(request.POST)
            logger.debug(form.errors)
    # GET request
    else:
        form = ReservationForm(location)
    # pass the rate for each room to the template so we can update the cost of
    # a reservation in real time.
    today = timezone.localtime(timezone.now())
    month = request.GET.get("month")
    year = request.GET.get("year")
    start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
    rooms = location.rooms_with_future_availability()
    return render(
        request,
        'reservation.html',
        {
            'form': form,
            'max_days': location.max_reservation_days,
            'location': location,
            'rooms': rooms,
            'prev_month': prev_month,
            'next_month': next_month,
            'month': month
        }
    )

def room(request, location_slug, room_id):
    return render(request, 'reservation.html')
