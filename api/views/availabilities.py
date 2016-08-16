from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from api.utils.http import JSONResponse
from api.commands.availabilities import *

from core.models import Availability
from core.serializers import AvailabilitySerializer

@csrf_exempt
def availabilities(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        command = AddAvailabilityChange(request.user, **data)
        if command.execute():
            return JSONResponse(command.result().serialize(), status=201)
        return JSONResponse(command.result().serialize(), status=400)
    else:
        return HttpResponseNotFound("404 not found")


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
