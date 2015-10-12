import json
from django.utils import timezone
from django.shortcuts import render
from gather.models import Event
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.safestring import SafeString
from django.utils.html import strip_tags
from django.conf import settings

from core.models import Location, UserProfile, MaypiDoor, MaypiDoorCode
from maypi import maypi_api

import logging

logger = logging.getLogger(__name__)

def index(request):
	recent_events = Event.objects.order_by('-start')[:10]
	locations = Location.objects.all()
	location_list = []
	for location in locations:
		if location.public:
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

def robots(request):
	content = "User-agent: *\n"
	for l in Location.objects.all():
		content += "Disallow: /locations/%s/team/\n" % l.slug
		content += "Disallow: /locations/%s/community/\n" % l.slug
		content += "Disallow: /locations/%s/reservation/create/\n" % l.slug
		content += "Disallow: /locations/%s/events/create/\n" % l.slug
	return HttpResponse(content, content_type="text/plain")
	
@csrf_exempt
def maypi(request):
	response = "No Data"
	if request.method == 'POST' and 'data' in request.POST:
		try:
			# Find the door they are talking about
			door_id = request.POST.get("door_id")
			door = MaypiDoor.objects.get(pk=door_id)

			# Unpack the data they sent
			data = request.POST.get("data")
			posted_data = maypi_api.unwrap_data(data, api_key=door.api_key)
			logger.info("Maypi sync from %s:%s" % (door.location, door.description))
			#logger.debug("Mayp sync data raw: %s" % data)
			logger.debug("Mayp sync data: %s" % posted_data)
			
			# TODO 
			# - Check for the give-me-all-your-door-codes command
			# - Build up a big json with all the door codes
			# - Send it back
			for code in MaypiDoorCode.objects.all():
				pass
			
			# For now just return the shit we got
			response = posted_data
			
			# Update the sync clock on success
			door.sync_ts = timezone.now()
			door.save()
		except Exception as e:
			print e
			response = "Invalid Data Provided"

	return HttpResponse(response, content_type="application/json")
