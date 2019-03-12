from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from modernomad.core.models import Location, UserProfile, Resource
from gather.models import Event
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from django.conf import settings
import json
from django.utils.html import strip_tags

def index(request):
    recent_events = Event.objects.order_by('-start')[:10]
    locations = Location.objects.filter(visibility='public')
    context = {'locations': locations, 'recent_events': recent_events}
    return render(request, "index.html", context)

def about(request):
    return render(request, "about.html")

def drft(request):
    rooms = Resource.objects.all
    return render(request, "drft.html", {'rooms': rooms})

def host(request):
    return render(request, "host.html")

def membership(request):
    return render(request, "membership.html")

def stay(request):
    return render(request, "stay.html")

def ErrorView(request):
    return render(request, '404.html')

def robots(request):
    content = "User-agent: *\n"
    for l in Location.objects.all():
        content += "Disallow: /locations/%s/team/\n" % l.slug
        content += "Disallow: /locations/%s/community/\n" % l.slug
        content += "Disallow: /locations/%s/booking/create/\n" % l.slug
        content += "Disallow: /locations/%s/events/create/\n" % l.slug
    return HttpResponse(content, content_type="text/plain")
