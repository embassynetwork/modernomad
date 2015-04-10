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
from gather.models import Event, EventAdminGroup, EventSeries
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from gather.emails import new_event_notification, event_approved_notification, event_published_notification
import logging

logger = logging.getLogger(__name__)

Location = get_model(*settings.LOCATION_MODEL.split(".", 1))

class LocationNotUniqueException(Exception):
	pass

def get_location(location_slug=None):
	if location_slug:
		location = Location.objects.get(slug=location_slug)
	else:
		if Location.objects.count() == 1:
			# the single object might not have pk=1 if a locationw as
			# previously created and then deleted, so by using the all() (after
			# checking there is only one location object) we aren't assuming
			# any particular id. 
			location = Location.objects.all()[0]
		else:
			raise LocationNotUniqueException("You did not specify a location and yet there is more than one location defined. Please specify a location.")
	return location

def event_guide(request, location_slug=None):
	location = get_location(location_slug)
	return render(request, 'gather_event_guide.html')

def create_event(request, location_slug=None):
	location = get_location(location_slug)
	current_user = request.user
	logger.debug("create_event: location:%s, user:%s" % (location, current_user))

	# if the user doesn't have a proper profile, then make sure they extend it first
	# TODO FIXME This is a direct dependency on an external app (the core app where the UserProfile model lives) 
	print current_user.id
	if current_user.id == None :
		messages.add_message(request, messages.INFO, 'We want to know who you are! Please create a profile before submitting an event.')
		return HttpResponseRedirect('/people/register/?next=/events/create/')
	elif current_user.is_authenticated and ((not current_user.profile.bio) or (not current_user.profile.image)):
		messages.add_message(request, messages.INFO, 'We want to know a bit more about you! Please complete your profile before submitting an event.')
		return HttpResponseRedirect('/people/%s/edit/' % current_user.username)

	other_users = User.objects.exclude(id=current_user.id)
	# get a list of users so that those creating an event can select from
	# existing users as event co-organizers
	user_list = [u.username for u in other_users]
	location_admin_group = EventAdminGroup.objects.get(location=location)
	if current_user in location_admin_group.users.all():
		is_event_admin = True
	else:
		is_event_admin = False

	if request.method == 'POST':
		logger.debug("create_event: POST=%s" % request.POST)
		form = EventForm(request.POST, request.FILES)
		if form.is_valid():
			event = form.save(commit=False)
			event.creator = current_user
			# associate this event with a specific location and admin group
			event.location = location
			event.admin = location_admin_group
			event.save()
			co_organizers = form.cleaned_data.get('co_organizers')
			# always make sure current user is an organizer
			event.organizers.add(current_user)
			event.organizers.add(*co_organizers)
			# organizers should be attendees by default, too. 
			event.attendees.add(current_user)
			event.save()

			new_event_notification(event, location)

			messages.add_message(request, messages.INFO, 'The event has been created.')
			return HttpResponseRedirect(reverse('gather_view_event', args=(event.location.slug, event.id, event.slug)))
		else:
			print "form error"
			print form.errors

	else:
		form = EventForm()
	return render(request, 'gather_event_create.html', {'form': form, 'current_user': current_user, 'user_list': json.dumps(user_list), 'is_event_admin': is_event_admin, 'location': location})

@login_required
def edit_event(request, event_id, event_slug, location_slug=None):
	location = get_location(location_slug)
	current_user = request.user
	other_users = User.objects.exclude(id=current_user.id)
	user_list = [u.username for u in other_users]
	event = Event.objects.get(id=event_id)
	if not (request.user.is_authenticated() and request.user in event.organizers.all()):
		return HttpResponseRedirect("/")

	if request.method == 'POST':
		form = EventForm(request.POST, request.FILES, instance=event)
		if form.is_valid():
			event = form.save(commit=False)
			co_organizers = form.cleaned_data.get('co_organizers')
			# always make sure current user is an organizer
			event.organizers.add(current_user)
			event.organizers.add(*co_organizers)
			event.save()
			messages.add_message(request, messages.INFO, 'The event has been saved.')
			return HttpResponseRedirect(reverse('gather_view_event', args=(event.location.slug, event.id, event.slug)))
		else:
			print "form error"
			print form.errors

	else:
		# format the organizers as a string for use with the autocomplete field
		other_organizers = event.organizers.exclude(id=current_user.id)
		other_organizer_usernames = [u.username for u in other_organizers]
		other_organizer_usernames_string = ",".join(other_organizer_usernames)
		print event.organizers.all()
		form = EventForm(instance=event, initial={'co_organizers': other_organizer_usernames_string})
	return render(request, 'gather_event_edit.html', {'form': form, 'current_user': current_user, 'event_id': event_id, 'event_slug': event_slug, 'user_list': json.dumps(user_list), 'location': location})

def view_event(request, event_id, event_slug, location_slug=None):
	# XXX should we double check the associated location here? currently the
	# assumption is that if an event is being viewed under a specific location
	# that that will be reflected in the URL path. 
	try:
		event = Event.objects.get(id=event_id)
	except:
		print 'event not found'
		return HttpResponseRedirect('/404')

	location = get_location(location_slug)
	# if the slug has changed, redirect the viewer to the correct url (one
	# where the url matches the current slug)
	if event.slug != event_slug:
		print 'event slug has changed'
		# there's some tomfoolery here since we don't know for sure if the app
		# is being used in a project that specifies the location as part of the
		# url. probably a better way to do this...
		return HttpResponseRedirect(reverse('gather_view_event', args=(event.location.slug, event.id, event.slug)))

	# is the event in the past?
	today = timezone.now()
	print event.end
	if event.end < today:
		past = True
	else:
		past = False

	# set up for those without accounts to RSVP
	if request.user.is_authenticated():
		current_user = request.user
		new_user_form = None
		login_form = None
		location_event_admin = EventAdminGroup.objects.get(location=location)
		if request.user in location_event_admin.users.all():
			user_is_event_admin = True
		else:
			user_is_event_admin = False
	else:
		current_user = None
		new_user_form = NewUserForm()
		login_form = AuthenticationForm()
		user_is_event_admin = False

	# this is counter-intuitive - private events are viewable to those who have
	# the link. so private events are indeed shown to anyone (once they are approved). 
	if (event.status == 'live' and event.private) or event.is_viewable(current_user):
		if current_user and current_user in event.organizers.get_query_set():
			user_is_organizer = True
		else:
			user_is_organizer = False
		num_attendees = len(event.attendees.all())
		# only meaningful if event.limit > 0
		spots_remaining = event.limit - num_attendees
		event_email = 'event%d@%s.%s' % (event.id, event.location.slug, settings.LIST_DOMAIN)
		domain = Site.objects.get_current().domain
		return render(request, 'gather_event_view.html', {'event': event, 'current_user': current_user, 
			'user_is_organizer': user_is_organizer, 'new_user_form': new_user_form, "event_email": event_email, "domain": domain,
			'login_form': login_form, "spots_remaining": spots_remaining, 'user_is_event_admin': user_is_event_admin, 
			"num_attendees": num_attendees, 'in_the_past': past, 'endorsements': event.endorsements.all(), 'location': location})

	else:
		return HttpResponseRedirect('/404')


def upcoming_events_all_locations(request):
	''' if a site supports multiple locations this page can be used to show
	events across all locations.'''
	if request.user.is_authenticated():
		current_user = request.user
	else:
		current_user = None
	today = datetime.datetime.today()
	all_upcoming = Event.objects.upcoming(current_user = request.user)
	culled_upcoming = []
	for event in all_upcoming:
		if event.is_viewable(current_user):
			culled_upcoming.append(event)

	# show 10 events per page
	paged_upcoming = Paginator(culled_upcoming, 10) 
	page = request.GET.get('page')
	try:
		events = paged_upcoming.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		events = paged_upcoming.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		events = paged_upcoming.page(paginator.num_pages)

	return render(request, 'gather_events_list.html', {"events": events, 'current_user': current_user, 'page_title': 'Upcoming Events'})



def upcoming_events(request, location_slug=None):
	''' upcoming events limited to a specific location (either the one
	specified or the default single location).'''
	if request.user.is_authenticated():
		current_user = request.user
	else:
		current_user = None
	today = datetime.datetime.today()
	location = get_location(location_slug)
	all_upcoming = Event.objects.upcoming(current_user = request.user, location=location)
	culled_upcoming = []
	for event in all_upcoming:
		if event.is_viewable(current_user):
			culled_upcoming.append(event)

	# show 10 events per page
	paged_upcoming = Paginator(culled_upcoming, 10) 
	page = request.GET.get('page')
	try:
		events = paged_upcoming.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		events = paged_upcoming.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		events = paged_upcoming.page(paginator.num_pages)

	return render(request, 'gather_events_list.html', {"events": events, 'current_user': current_user, 'page_title': 'Upcoming Events', 'location': location})


def user_events(request, username):
	user = User.objects.get(username=username)
	today = timezone.now()
	events_organized_upcoming = user.events_organized.all().filter(end__gte = today).order_by('start')
	events_attended_upcoming = user.events_attending.all().filter(end__gte = today).order_by('start')
	events_organized_past = user.events_organized.all().filter(end__lt = today).order_by('-start')
	events_attended_past = user.events_attending.all().filter(end__lt = today).order_by('-start')
	return render(request, 'gather_user_events_list.html', {
		'events_organized_upcoming': events_organized_upcoming, 
		'events_attended_upcoming': events_attended_upcoming, 
		'events_organized_past': events_organized_past, 
		'events_attended_past': events_attended_past, 
		'current_user': user, 'page_title': 'Upcoming Events', 
	})


@login_required
def needs_review(request, location_slug=None):
	location = get_location(location_slug)
	# if user is not an event admin at this location, redirect
	location_admin_group = EventAdminGroup.objects.get(location=location)
	if not request.user.is_authenticated() or (request.user not in location_admin_group.users.all()):
		return HttpResponseRedirect('/')
		
	# upcoming events that are not yet live
	today = timezone.now()
	events_pending = Event.objects.filter(status=Event.PENDING).filter(end__gte = today).filter(location=location)
	events_under_discussion = Event.objects.filter(status=Event.FEEDBACK).filter(end__gte = today).filter(location=location)
	return render(request, 'gather_events_admin_needing_review.html', {'events_pending': events_pending, 'events_under_discussion': events_under_discussion, 'location': location })

def past_events(request, location_slug=None):
	location = get_location(location_slug)
	if request.user.is_authenticated():
		current_user = request.user
	else:
		current_user = None
	today = datetime.datetime.today()
	# most recent first
	all_past = Event.objects.filter(start__lt = today).order_by('-start').filter(location=location)
	culled_past = []
	for event in all_past:
		if event.is_viewable(current_user):
			culled_past.append(event)
	# show 10 events per page
	paged_past = Paginator(culled_past, 10) 
	page = request.GET.get('page')
	try:
		events = paged_past.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		events = paged_past.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		events = paged_past.page(paginator.num_pages)

	return render(request, 'gather_events_list.html', {"events": events, 'user': current_user, 'page_title': 'Past Events', 'location': location})


def email_preferences(request, username, location_slug=None):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	
	u = User.objects.get(username=username)
	notifications = u.event_notifications
	if request.POST.get('event_reminders') == 'on':
		notifications.reminders = True
	else:
		notifications.reminders = False

	for location in Location.objects.all():
		weekly_updates = request.POST.get(location.slug)
		if weekly_updates == 'on' and location not in notifications.location_weekly.all():
			notifications.location_weekly.add(location)
		if weekly_updates == None and location in notifications.location_weekly.all():
			notifications.location_weekly.remove(location)

	notifications.save()
	print notifications.location_weekly.all()
	messages.add_message(request, messages.INFO, 'Your preferences have been updated.')
	return HttpResponseRedirect('/people/%s/' % u.username)

############################################
########### AJAX REQUESTS ##################


@login_required
def rsvp_event(request, event_id, event_slug, location_slug=None):
	location = get_location(location_slug)
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	user_id_str = request.POST.get('user_id')
	event = Event.objects.get(id=event_id)
	user = User.objects.get(pk=int(user_id_str))
	if user in event.organizers.all():
		user_is_organizer = True
	else:
		user_is_organizer = False
	if user not in event.attendees.all():
		event.attendees.add(user)
		event.save()
		num_attendees = event.attendees.count()
		spots_remaining = event.limit - num_attendees 
		return render(request, "snippets/rsvp_info.html", {"num_attendees": num_attendees, "spots_remaining": spots_remaining, "event": event, 'current_user': user, 'user_is_organizer': user_is_organizer, 'location': location });
		
	else:
		print 'user was aready attending'
	return HttpResponse(status=500); 

@login_required
def rsvp_cancel(request, event_id, event_slug, location_slug=None):
	location = get_location(location_slug)
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	user_id_str = request.POST.get('user_id')

	print 'event slug'
	print event_slug
	event = Event.objects.get(id=event_id)
	user = User.objects.get(pk=int(user_id_str))
	if user in event.organizers.all():
		user_is_organizer = True
	else:
		user_is_organizer = False

	if user in event.attendees.all():
		event.attendees.remove(user)
		event.save()
		num_attendees = event.attendees.count()
		spots_remaining = event.limit - num_attendees 
		return render(request, "snippets/rsvp_info.html", {"num_attendees": num_attendees, "spots_remaining": spots_remaining, "event": event, 'current_user': user, 'user_is_organizer': user_is_organizer, 'location': location });
	else:
		print 'user was not attending'
	return HttpResponse(status=500); 

def rsvp_new_user(request, event_id, event_slug, location_slug=None):
	location = get_location(location_slug)
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	print 'in rsvp_new_user'
	print request.POST
	# get email signup info and remove from form, since we tacked this field on
	# but it's not part of the user model. 
	weekly_updates = request.POST.get('email-notifications')
	if weekly_updates == 'on':
		weekly_updates = True
	else:
		weekly_updates = False
	print 'weekly updates?'
	print weekly_updates

	# create new user
	form = NewUserForm(request.POST)
	if form.is_valid():
		new_user = form.save()
		new_user.save()
		notifications = new_user.event_notifications
		if weekly_updates:
			# since the signup was related to a specific location we assume
			# they wanted weekly emails about the same location
			notifications.location_weekly.add(location)
		notifications.save()

		password = request.POST.get('password1')
		new_user = authenticate(username=new_user.username, password=password)
		login(request, new_user)
		# RSVP new user to the event
		event = Event.objects.get(id=event_id)
		event.attendees.add(new_user)
		print (event.attendees.all())
		event.save()
		messages.add_message(request, messages.INFO, 'Thanks! Your account has been created. Check your email for login info and how to update your preferences.')
		return HttpResponse(status=200)
	else:
		errors = json.dumps({"errors": form.errors})
		return HttpResponse(json.dumps(errors))

	return HttpResponse(status=500); 

def endorse(request, event_id, event_slug, location_slug=None):
	location = get_location(location_slug)
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	event = Event.objects.get(id=event_id)

	print request.POST
	endorser = request.user
	event.endorsements.add(endorser)
	event.save()
	endorsements = event.endorsements.all()
	return render(request, "snippets/endorsements.html", {"endorsements": endorsements, "current_user": request.user, 'location': location, 'event': event});

def event_approve(request, event_id, event_slug, location_slug=None):
	location = get_location(location_slug)
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location_event_admin = EventAdminGroup.objects.get(location=location)
	if request.user not in location_event_admin.users.all():
		return HttpResponseRedirect('/404')

	event = Event.objects.get(id=event_id)

	event.status = Event.READY
	event.save()
	if request.user in location_event_admin.users.all():
		user_is_event_admin = True
	else:
		user_is_event_admin = False
	if request.user in event.organizers.all():
		user_is_organizer = True
	else:
		user_is_organizer = False
	msg_success = "Success! The event has been approved."

	# notify the event organizers
	event_approved_notification(event, location)

	return render(request, "snippets/event_status_area.html", {'event': event, 'user_is_organizer': user_is_organizer, 'user_is_event_admin': user_is_event_admin})

def event_publish(request, event_id, event_slug, location_slug=None):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	location = get_location(location_slug)
	location_event_admin = EventAdminGroup.objects.get(location=location)
	if request.user not in location_event_admin.users.all():
		return HttpResponseRedirect('/404')

	event = Event.objects.get(id=event_id)

	print request.POST
	event.status = Event.LIVE
	event.save()
	if request.user in location_event_admin.users.all():
		user_is_event_admin = True
	else:
		user_is_event_admin = False
	if request.user in event.organizers.all():
		user_is_organizer = True
	else:
		user_is_organizer = False
	msg_success = "Success! The event has been published."

	# notify the event organizers and admins
	event_published_notification(event, location)

	return render(request, "snippets/event_status_area.html", {'location':location, 'event': event, 'user_is_organizer': user_is_organizer, 'user_is_event_admin': user_is_event_admin})

def new_user_email_signup(request, location_slug=None):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	print request.POST

	location = get_location(location_slug)
	# create new user
	form = NewUserForm(request.POST)
	if form.is_valid():
		new_user = form.save()
		new_user.save()
		notifications = new_user.event_notifications
		notifications.location_weekly.add(location)
		notifications.save()

		password = request.POST.get('password1')
		new_user = authenticate(username=new_user.username, password=password)
		login(request, new_user)
		messages.add_message(request, messages.INFO, 'Thanks! We\'ll send you weekly event updates for this location. You can update your preferences at any time on your <a href="/people/%s">profile</a> page' % new_user.username)
		return HttpResponse(status=200)
	else:
		errors = json.dumps({"errors": form.errors})
		return HttpResponse(json.dumps(errors))

	return HttpResponse(status=500); 
