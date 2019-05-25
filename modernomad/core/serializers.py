from datetime import timedelta
import datetime as dt

from django.utils import timezone
from rest_framework import serializers
import maya

from modernomad.core.models import CapacityChange
from modernomad.core.models import Location
from modernomad.core.models import Resource


class CapacityChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacityChange
        fields = ('id', 'start_date', 'resource', 'quantity', 'accept_drft')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        exclude = ['location']

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        request = self.context['request']
        try:
            params = request.query_params.dict()
        except AttributeError:
            # this is a django request and not a REST request
            params = request.GET.dict()

        arrive = maya.parse(params.get('arrive', dt.datetime.today())).date
        depart = maya.parse(params.get('depart', arrive + timedelta(days=13))).date

        availabilities = [
            {'date': date, 'quantity': quantity} for (date, quantity)
            in obj.daily_availabilities_within(arrive, depart)
        ]
        representation['availabilities'] = availabilities
        representation['hasFutureDrftCapacity'] = obj.has_future_drft_capacity()
        representation['maxBookingDays'] = obj.location.max_booking_days
        return representation
