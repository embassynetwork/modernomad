from core.models import Location

def network_locations(request):
	return {'network_locations': Location.objects.all() }
