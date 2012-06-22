from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource

from django.contrib.auth.models import User
from core.models import House, Resource, UserProfile, Endorsement

# XXX TODO 
# add real authentication. 
# implement CORS https://gist.github.com/426829
# - how to set default header in tasty-oie response OR how to integrate middleware?

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

# available at /endorsements
class EndorsementsResource(ModelResource):
	class Meta:
		queryset = Endorsement.objects.all()
		authorization = Authorization()
		always_return_data = True

