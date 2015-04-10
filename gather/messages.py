from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib.sites.models import Site
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from PIL import Image
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from gather.forms import EventForm, NewUserForm
import datetime
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from gather.models import Event
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import json
from gather import WAIT_FOR_FEEDBACK

