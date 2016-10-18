from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from api.utils.http import JSONResponse
from api.commands.capacities import *

from core.models import CapacityChange
from core.serializers import CapacityChangeSerializer


@csrf_exempt
def capacities(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        command = UpdateOrAddCapacityChange(request.user, **data)
        command.execute()
        return JSONResponse(command.result().serialize(), status=command.result().http_status())
    else:
        return HttpResponseNotFound("404 not found")


@csrf_exempt
def capacity_detail(request, capacity_id):
    try:
        capacity = CapacityChange.objects.get(pk=capacity_id)
    except CapacityChange.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CapacityChangeSerializer(capacity)
        return JSONResponse(serializer.data)

    elif request.method == 'DELETE':
        command = DeleteCapacityChange(request.user, capacity=capacity)
        command.execute()
        return JSONResponse(command.result().serialize(), status=command.result().http_status())
