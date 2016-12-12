from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import CapacityChange


# Serializers define the API representation.
class CapacityChangeSerializer(serializers.ModelSerializer):
    '''Includes simple default implementations for the create() and update() methods.'''
    class Meta:
        model = CapacityChange
        fields = ('id', 'start_date', 'resource', 'quantity', 'accept_drft')
