from core.models import Location
import re

def network_locations(request):
	return {'network_locations': Location.objects.all() }

def location_variables(request):
	match = re.match(r'^/locations/(?P<location_slug>[^/]*)/.*', request.path)
	print "context variable"
	print match.group('location_slug')
	if match:
		location_slug = match.group('location_slug')
		location = Location.objects.get(slug = location_slug)
		location_about_path = 'locations/%s/about/' % location_slug
		location_stay_path = 'locations/%s/stay/' % location_slug
		return {'location': location, 'location_about_path': location_about_path, 'location_stay_path': location_stay_path}
	return {}
