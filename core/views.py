from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration import signals
import registration.backends.default
from registration.models import RegistrationProfile
from core.forms import ReservationForm, ExtendedUserCreationForm, CombinedUserForm
from django.core.mail import send_mail
from django.core import urlresolvers
import datetime
from django.contrib import messages

from core.models import House, UserProfile, Reservation

def logout(request):
	logout(request)
	messages.add_message(request, messages.INFO, 'You have been logged out.')
	return HttpResponseRedirect("/")

@login_required
def ListUsers(request):
	users = User.objects.filter(is_active=True)
	return render(request, "user_list.html", {"users": users})

@login_required
def GetUser(request, username):
	user = User.objects.get(username=username)
	reservations = Reservation.objects.filter(user=user).exclude(status='deleted')
	past_reservations = []
	upcoming_reservations = []
	for reservation in reservations:
		if reservation.arrive >= datetime.date.today():
			upcoming_reservations.append(reservation)
		else:
			past_reservations.append(reservation)
	return render(request, "user_details.html", {"u": user, 
		"past_reservations": past_reservations, "upcoming_reservations": upcoming_reservations})

def ListHouses(request):
	houses = House.objects.all()
	return render(request, "house_list.html", {"houses": houses})

def GetHouse(request, house_id):
	house = House.objects.get(id=house_id)
	return render(request, "house_details.html", {"house": house})

def ReservationSubmit(request):
	if request.method == 'POST':
		POST = request.POST.copy()
		if not request.user.is_authenticated():
			print POST
			user_data = {
				'username': POST['username'],
				'first_name': POST['first_name'],
				'last_name': POST['last_name'],
				'password1': POST['password1'],
				'password2': POST['password2'],
				'email': POST['email'],
			}
			user_form = ExtendedUserCreationForm(user_data)
		
			POST.pop('username')
			POST.pop('first_name')
			POST.pop('last_name')
			POST.pop('email')
			POST.pop('password1') 
			POST.pop('password2') 
		
			if user_form.is_valid():   
				# create the user and log them in
				user_form.save()
				user = authenticate(username=user_data['username'], password=user_data['password1'])
				if user is not None:
					login(request, user)
					print "user %s created and logged in" % user.username
				else:
					print "this should not have happened. new user was created but did not authenticate."           
			else:
				print "user form was not valid"
				print user_form.errors

		form = ReservationForm(POST)
		if form.is_valid() and request.user.is_authenticated():
			reservation = form.save(commit=False)
			reservation.user = request.user

			reservation.save()            
			messages.add_message(request, messages.INFO, 'Thanks! Your reservation was created. You will receive an email when it has been reviewed. You can still modify your reservation.')
			return HttpResponseRedirect('/reservation/%d' % reservation.id)

	# GET request
	else: 
		form = ReservationForm()
		if not request.user.is_authenticated():
			print "creating new user form"
			user_form = ExtendedUserCreationForm()

	# default - render either the bound form with errors or the unbound form    
	if request.user.is_authenticated():
		return render(request, 'reservation.html', {'form': form})
	else:
		return render(request, 'reservation.html', {'form': form, 'user_form': user_form})

@login_required
def ReservationDetail(request, reservation_id):
	try:
		reservation = Reservation.objects.get(id=reservation_id)
		if reservation.status == 'deleted':
			raise Reservation.DoesNotExist
	except Reservation.DoesNotExist:
		msg = 'The reservation you requested do not exist'
		messages.add_message(request, messages.ERROR, msg)
		return HttpResponseRedirect('/404')
	else:
		if reservation.arrive > datetime.date.today():
			past = False
		else:
			past = True
		return render(request, "reservation_detail.html", {"reservation": reservation, "past":past})


@login_required
def UserEdit(request, username):
	user = UserProfile.objects.get(user__username=username)
	if request.user.is_authenticated() and request.user.id == user.id:
		if request.method == "POST":
			form = CombinedUserForm(request.POST, instance=user)
			if form.is_valid():
				form.save()
				client_msg = "Your profile has been updated."
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect("/people/%s" % username)
		else:
			form = CombinedUserForm(instance=user)
		
		return render(request, 'user_edit.html', {'form': form})
	return HttpResponseRedirect("/")


@login_required
def ReservationEdit(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	# need to pull these dates out before we pass the instance into
	# the ReservationForm, since it (apparently) updates the instance 
	# immediately (which is weird, since it hasn't validated the form 
	# yet!)
	original_arrive = reservation.arrive
	original_depart = reservation.depart
	if request.user.is_authenticated() and request.user == reservation.user:
		if request.method == "POST":
			# don't forget to specify the "instance" argument or a new object will get created!
			form = ReservationForm(request.POST, instance=reservation)
			if form.is_valid():

				# if the dates have been changed, and the reservation isn't still 
				# pending to begin with, notify an admin and go back to pending. 
				if (reservation.status != 'pending' and 
					(reservation.arrive != original_arrive or reservation.depart != original_depart)):

					print "reservation date was changed. updating status."
					reservation.status = "pending"
					
					# notify house_admins by email
					house_admins = User.objects.filter(groups__name='house_admin')
					subject = "[Embassy SF] Reservation Updated, %s %s, %s - %s" % (reservation.user.first_name, 
						reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
					sender = "stay@embassynetwork.com"
					domain = Site.objects.get_current().domain
					admin_path = urlresolvers.reverse('admin:core_reservation_change', args=(reservation.id,))
					text = '''Howdy, 

A reservation has been updated and requires your review. 

You can view, approve or deny this request at %s%s.''' % (domain, admin_path)
					# XXX TODO this is terrible. should have an alias and let a mail agent handle this!
					for admin in house_admins:
						recipient = [admin.email,]
						send_mail(subject, text, sender, recipient) 

					client_msg = 'Your reservation was updated and the new dates will be reviewed for availability.'
				else:
					client_msg = 'Your reservation was updated.'
				# save the instance *after* the status has been updated as needed.  
				form.save()
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect("/reservation/%s" % reservation_id)
		else:
			form = ReservationForm(instance=reservation)
		
		return render(request, 'reservation_edit.html', {'form': form, 
			'reservation_id': reservation_id,
			'arrive': reservation.arrive,
			'depart': reservation.depart,
			})

	else:
		return HttpResponseRedirect("/")


@login_required
def ReservationConfirm(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	if (request.user.is_authenticated() and request.user == reservation.user 
		and request.method == "POST" and reservation.status == 'approved'):

		reservation.status = 'confirmed'
		reservation.save()

		messages.add_message(request, messages.INFO, 'Thank you! Check your email for further details.')
		return HttpResponseRedirect("/reservation/%s" % reservation_id)

	else:
		return HttpResponseRedirect("/")

@login_required
def ReservationDelete(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	if (request.user.is_authenticated() and request.user == reservation.user 
		and request.method == "POST"):
		reservation.status = 'deleted'
		reservation.save()

		messages.add_message(request, messages.INFO, 'Your reservation has been canceled.')
		username = reservation.user.username
		return HttpResponseRedirect("/people/%s" % username)

	else:
		return HttpResponseRedirect("/")


class RegistrationBackend(registration.backends.default.DefaultBackend):
	'''A registration backend that supports capturing user profile
	information during registration.'''
	
	@transaction.commit_on_success
	def register(self, request, **cleaned_data):
		'''Register a new user, saving the User and UserProfile data.'''
		# We can't use RegistrationManager.create_inactive_user()
		# because it doesn't play nice with saving other information
		# in the same transaction.
		user = User(is_active=False)
		for field in user._meta.fields:
			if field.name in cleaned_data:
				setattr(user, field.name, cleaned_data[field.name])
		user.save()

		profile = UserProfile(user=user)
		for field in profile._meta.fields:
			if field.name in cleaned_data:
				setattr(profile, field.name, cleaned_data[field.name])
		profile.save()

		registration_profile = RegistrationProfile.objects.create_profile(user)
		registration_profile.send_activation_email(Site.objects.get_current())

		signals.user_registered.send(sender=self.__class__, user=user, request=request)
