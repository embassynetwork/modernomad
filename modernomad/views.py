from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from core.models import Location
from gather.models import Event
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import SafeString
from django.conf import settings


def index(request):
	return render(request, "index.html")

def about(request):
	return render(request, "about.html")

def stay(request):
	return render(request, "stay.html")

def ErrorView(request):
	return render(request, '404.html')



