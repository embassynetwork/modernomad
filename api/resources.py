from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource
from tastypie import fields
import datetime

from django.contrib.auth.models import User
from core.models import House, Resource, UserProfile, Reservation

# XXX TODO 
# add real authentication. 

class UserAuth(Authentication):
	''' use as authorization for resources where the user must be
	authenticated'''
	def is_authenticated(self, request, **kwargs):
		# XXX this is pseudocode
		if request.user and request.user.id in request.house.admins:
			return True
		else:
			return False

# exposes /api/houses, /api/houses/<id>, /api/houses/schema/,
# /api/houses/set/1;10/. 
# allows full access to CRUD, exposes all fields. 
class HousesResource(ModelResource):
	# TODO (JKS) include resources with house object
	class Meta:
		queryset = House.objects.all()
		authorization = Authorization()
		always_return_data = True

# available at /locations
class LocationsResource(ModelResource):
	class Meta:
		queryset = House.objects.all()
		list_allowed_methods = ['get']
		detail_allowed_methods = []
		fields = ['latLong', 'id']
		authorization = Authorization()
		always_return_data = True

# available at /resources
class ResourcesResource(ModelResource):
	class Meta:
		queryset = Resource.objects.all()
		authorization = Authorization()
		always_return_data = True

# available at /users
class UsersResource(ModelResource):
	class Meta:
		queryset = UserProfile.objects.all()
		authorization = Authorization()
		always_return_data = True

class UserBaseResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		authorization = Authorization()
		always_return_data = True

class UpcomingResource(ModelResource):
	class Meta:
		queryset = Reservation.objects.all().order_by('arrive')

	def alter_list_data_to_serialize(self, request, data_dict):
		if isinstance(data_dict, dict):
			if 'meta' in data_dict: 
				# Get rid of the "meta". 
				del(data_dict['meta'])

			# add in our custom pre-amble
			today = str(datetime.date.today()).replace("-", ",")
			data_dict["timeline"] = {
				"headline":"Embassy SF Upcoming Guests", 
				"type":"default", 
				"text":"Read all about it!", 
				"startDate": today,
				"date": [] 
			} 

			# move the individual timeline objects within the timeline pre-amble 
			data_dict["timeline"]["date"] = data_dict["objects"] 
			del(data_dict["objects"]) 

		return data_dict


	def dehydrate(self, bundle):
		headline_text = "<h3>%s %s</h3>" % (bundle.obj.user.first_name, bundle.obj.user.last_name)
		body_text = "<p class='timeline-tags'>%s</p><p><b>Projects: </b>%s</p><p><b>Sharing: </b>%s</p><p><b>Discussion: </b>%s</p><p><b>Purpose: </b>%s</p>" % (
			bundle.obj.tags, bundle.obj.projects, bundle.obj.sharing, bundle.obj.discussion, bundle.obj.purpose)
		res_data = {
	        "startDate":str(bundle.obj.arrive).replace("-", ","),
			"endDate":str(bundle.obj.depart).replace("-", ","),
	        "headline":headline_text,
	        "text": body_text
	    }

		bundle.data = res_data
		return bundle


