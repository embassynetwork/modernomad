from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def old_user_bookings_redirect(request, username):
    return redirect('user_bookings', username=username, permanent=True)

@login_required
def reservation_redirect(request, location_slug, rest_of_path):
    return redirect('/locations/%s/booking/%s/' % (location_slug, rest_of_path), permanent=True)



