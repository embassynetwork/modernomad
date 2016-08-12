from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import Availability

# For serializing model classes
# Craig: I think that this should really be seperated from core. It's needed
#        by both the API and the web interface at the moment.

# Serializers define the API representation.
class AvailabilitySerializer(serializers.ModelSerializer):
	'''Includes simple default implementations for the create() and update() methods.'''
	class Meta:
		model = Availability
		fields = ('id', 'start_date', 'resource', 'quantity' )
