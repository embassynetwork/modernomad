from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from core.forms import SignupForm
from core.models import User

def ListUsers(request):
    return HttpResponse("Show all users")

def ListLocations(request):
    return render_to_response("locations.html")

def GetUser(request, user_id):
   return HttpResponse("This is a specific user page")

def SignupUser(request):
    if request.method == "POST":
        f = SignupForm(request.POST, request.FILES) 
	if f.is_valid():
	    f.save()
	    return HttpResponseRedirect('/thanks')
    else:
        f = SignupForm()
    return render_to_response('signup.html', 
			      {'f': f}, context_instance=RequestContext(request))
