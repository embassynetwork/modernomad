from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
import logging
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from modernomad.core.models import Use, Location

@login_required
def UseDetail(request, use_id, location_slug):
    location = get_object_or_404(Location, slug=location_slug)
    try:
        use = Use.objects.get(id=use_id)
        if not use:
            raise Use.DoesNotExist
    except Use.DoesNotExist:
        msg = 'The use you requested does not exist'
        messages.add_message(request, messages.ERROR, msg)
        return HttpResponseRedirect('/404')
    # make sure the user is either an admin, resident or the use holder
    # (we can't use the decorator here because the user themselves also has to
    # be able to see the page).
    if ((request.user == use.user) or
            (request.user in location.house_admins.all()) or
            (request.user in location.readonly_admins.all()) or
            (request.user in location.residents.all())):
        if use.arrive >= datetime.date.today():
            past = False
        else:
            past = True

        domain = Site.objects.get_current().domain

        # users that intersect this stay
        users_during_stay = []
        uses = Use.objects.filter(status="confirmed").filter(location=location).exclude(depart__lt=use.arrive).exclude(arrive__gt=use.depart)
        for use in uses:
            if use.user not in users_during_stay:
                users_during_stay.append(use.user)
        for member in location.residents.all():
            if member not in users_during_stay:
                users_during_stay.append(member)

        has_future_drft_capacity = False
        drft_balance = 0
        try:
            drft = Currency.objects.get(name="DRFT")
            accounts = Account.objects.filter(owners=use.user).filter(currency = drft)
            for a in accounts:
                if a.get_balance() > 0:
                    drft_balance += a.get_balance()

            if use.resource.drftable_between(use.arrive, use.depart):
                has_future_drft_capacity = True
        except:
            # continues silently if no DRFT and room backing have not been
            # setup.
            pass

        return render(
            request,
            "use_detail.html",
            {
                "use": use,
                "past": past,
                'location': location,
                "domain": domain,
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                "contact": location.from_email(),
                'users_during_stay': users_during_stay,
                'drft_balance': drft_balance,
                'has_future_drft_capacity': has_future_drft_capacity,
            }
        )
    else:
        messages.add_message(request, messages.INFO, "You do not have permission to view that use")
        return HttpResponseRedirect('/404')


