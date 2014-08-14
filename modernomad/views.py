from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from core.models import Location, UserProfile
from gather.models import Event
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from django.conf import settings
import json
from django.utils.html import strip_tags

def index(request):
	recent_events = Event.objects.order_by('-start')[:10]
	locations = Location.objects.all()
	location_list = []
	for location in locations:
		location_list.append({
				'name': location.name,
				'latitude': location.latitude,
				'longitude': location.longitude,
				'short_description': strip_tags(location.short_description[:200])+"...",
				'image': location.image.url,
				'url': location.get_absolute_url(),
				'has_availability': location.has_availability(),
				'num_rooms': location.rooms.count()

		})
	return render(request, "index.html", {'location_list': json.dumps(location_list), 'recent_events': recent_events})

def about(request):
	return render(request, "about.html")

def host(request):
	return render(request, "host.html")

def membership(request):
	return render(request, "membership.html")

def stay(request):
	return render(request, "stay.html")

def ErrorView(request):
	return render(request, '404.html')



