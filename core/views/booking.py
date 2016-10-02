from django.shortcuts import render

# def BookingSubmit(request, location_slug):
#     location = get_object_or_404(Location, slug=location_slug)
#     if request.method == 'POST':
#         form = BookingUseForm(location, request.POST)
#         if form.is_valid():
#             print 'form is valid'
#             comments = request.POST.get('comments')
#             use = form.save(commit=False)
#             use.location = location
#             booking = Booking(use=use, comments=comments)
#             # reset_rate also generates the bill.
#             if request.user.is_authenticated():
#                 use.user = request.user
#                 use.save()
#                 # we already set the value of 'use' when creating the Booking,
#                 # but it wasn't saved at that point, and Django complains about
#                 # a missing primary key here otherwise, so re-setting.
#                 booking.use = use
#                 booking.save()
#                 booking.reset_rate()
#                 new_booking_notify(booking)
#                 messages.add_message(
#                     request,
#                     messages.INFO,
#                     'Thanks! Your booking was submitted. You will receive an email when it has been reviewed. You may wish to <a href="/people/%s/edit/">update your profile</a> if your projects or ideas have changed since your last visit.' % booking.use.user.username
#                 )
#                 return HttpResponseRedirect(reverse('booking_detail', args=(location_slug, booking.id)))
#             else:
#                 booking_data = booking.serialize()
#                 request.session['booking'] = booking_data
#                 messages.add_message(request, messages.INFO, 'Thank you! Please make a profile to complete your booking request.')
#                 return HttpResponseRedirect(reverse('registration_register'))
#         else:
#             print 'form was not valid'
#             logger.debug(request.POST)
#             logger.debug(form.errors)
#     # GET request
#     else:
#         form = BookingUseForm(location)
#     pass the rate for each room to the template so we can update the cost of
#     a booking in real time.
#     today = timezone.localtime(timezone.now())
#     month = request.GET.get("month")
#     year = request.GET.get("year")
#     start, end, next_month, prev_month, month, year = get_calendar_dates(month, year)
#     rooms = location.rooms_with_future_capacity()
#     return render(
#         request,
#         'booking.html',
#         {}
#     )


def StayComponent(request, location_slug, room_id=None):
    return render(request, 'booking.html')
