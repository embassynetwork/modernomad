from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404

from jwt_auth.mixins import JSONWebTokenAuthMixin
from jwt_auth.compat import json
from core.models import *
from api.serializers import *

from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


# Create your views here.

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def availability_list_all(request):
	''' List or create availabilities for a specific resource.'''
	if request.method == 'GET':
		availabilities = Availability.objects.all()
		serializer = AvailabilitySerializer(availabilities, many=True)
		return JSONResponse(serializer.data)
	
@csrf_exempt
def availability_list(request, resource_id):
	''' List or create availabilities for a specific resource.'''
	if request.method == 'GET':
		resource = get_object_or_404(Resource, id=resource_id)
		availabilities = Availability.objects.filter(resource=resource)
		serializer = AvailabilitySerializer(availabilities, many=True)
		return JSONResponse(serializer.data)
	
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = AvailabilitySerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def availability_detail(request, availability_id):
    ''' Retrieve, update or delete an availability.'''
    try:
        availability = Availability.objects.get(pk=availability_id)
    except Availability.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AvailabilitySerializer(availability)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AvailabilitySerializer(availability, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        availability.delete()
        return HttpResponse(status=204)

def api_test(request):
	return HttpResponse(200)

class CurrentLocationOccupancies(JSONWebTokenAuthMixin, View):
	''' Expects a proper JWT token to be passed into the header. If valid, the
	user will be treated as logged in. If not, the method will return 401
	unauthorized.'''

	def where(self, user):
		''' tell us where the user is today. this method is necessarily...
		opinionated. it treats guest bookings >> residence >> membership.'''

		today = timezone.now()
		reservations = Reservation.objects.filter(user=user, depart__gte=today, arrive__lte=today)
		residences = user.residences.all()
		subscriptions = Subscription.objects.active_subscriptions().filter(user=user)

		user_location = None
		if reservations:
			# take the first one...
			user_location = reservations[0].location

		elif residences:
			# just take the first one...
			user_location = residences[0]

		elif subscriptions:
			# just take the first one...
			user_location = subscriptions[0].location

		return user_location


	def get(self, request, username):
		try:
			user = User.objects.get(username=username)
		except:
			return HttpResponse(status=404)

		location = self.where(user)
		print 'location'
		print location
		data = {}

		if location:
			# people today includes residents, guests and subscribers. does not
			# currently include event attendees. 
			people_today = location.people_today()
			print 'people today'
			print people_today

			data['location'] = {'id': location.id, 'name': location.name}
			occupants = []
			domain = "https://" + Site.objects.get_current().domain
			for u in people_today:
				try:
					profile_img = domain + u.profile.image.url
				except:
					profile_img = None

				user_data = {
						'id': u.id,
						'name': "%s %s" % (u.first_name, u.last_name),
						'username': u.username, 
						'avatar': profile_img,
						'profile_url': domain + reverse('user_detail', args=(u.username,)),
					}
				occupants.append(user_data)
			data['location']['occupants'] = occupants

		json_data = json.dumps(data)
		return HttpResponse(json_data)
