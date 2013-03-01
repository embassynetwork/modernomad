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
from core.forms import ReservationForm, UserProfileForm
from django.core.mail import send_mail
from django.core import urlresolvers
import datetime
from django.contrib import messages

from core.models import UserProfile, Reservation, Room

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

def get_reservation_form_for_perms(request, post, instance):
	if post == True:
		if instance:
			form = ReservationForm(request.POST, instance=instance)
		else:
			form = ReservationForm(request.POST)
	else:
		if instance:
			form = ReservationForm(instance=instance)
		else:
			form = ReservationForm()
	# ensure we only show official guest rooms unless the user is a house admin. 
	if not request.user.groups.filter(name='house_admin'):
		form.fields['room'].queryset = Room.objects.filter(primary_use="guest")
	return form

@login_required
def ReservationSubmit(request):
	if request.method == 'POST':
		form = get_reservation_form_for_perms(request, post=True, instance=False)

		if form.is_valid():
			reservation = form.save(commit=False)
			reservation.user = request.user
			# this view is used only for submitting new reservations. if the
			# user is not a house admin, the default status should always be
			# set to "pending."
			if not request.user.groups.filter(name='house_admin'):
				reservation.status = "pending"
			reservation.save()
			if reservation.hosted:
				messages.add_message(request, messages.INFO, 'The reservation has been created. You can modify the reservation below.')
			else:
				messages.add_message(request, messages.INFO, 'Thanks! Your reservation was submitted. You will receive an email when it has been reviewed. Please <a href="/people/%s/edit/">update your profile</a> if your projects or other big ideas have changed since your last visit.<br><br>You can still modify your reservation.' % reservation.user.username)			
			return HttpResponseRedirect('/reservation/%d' % reservation.id)

	# GET request
	else: 
		form = get_reservation_form_for_perms(request, post=False, instance=False)

	# default - render either the bound form with errors or the unbound form    
	if request.user.groups.filter(name='house_admin'):
		is_house_admin = True
	else:
		is_house_admin = False
	return render(request, 'reservation.html', {'form': form, 'is_house_admin': is_house_admin})


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
	profile = UserProfile.objects.get(user__username=username)
	user = User.objects.get(username=username)
	if request.user.is_authenticated() and request.user.id == user.id:
		if request.method == "POST":
			profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
			if profile_form.is_valid(): 
				updated_user = profile_form.save()
				client_msg = "Your profile has been updated."
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect("/people/%s" % updated_user.username)
			else:
				print profile_form.errors
		else:
			profile_form = UserProfileForm(instance=profile)		
		return render(request, 'user_edit.html', {'profile_form': profile_form})
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

		if request.user.groups.filter(name='house_admin'):
			is_house_admin = True
		else:
			is_house_admin = False

		if request.method == "POST":
			# don't forget to specify the "instance" argument or a new object will get created!
			form = get_reservation_form_for_perms(request, post=True, instance=reservation)
			if form.is_valid():

				# if the dates have been changed, and the reservation isn't
				# still  pending to begin with, notify an admin and go back to
				# pending (unless it's hosted, then we don't generate an
				# email).
				if not reservation.hosted and (reservation.status != 'pending' and 
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

					client_msg = 'The reservation was updated and the new dates will be reviewed for availability.'
				else:
					client_msg = 'The reservation was updated.'
				# save the instance *after* the status has been updated as needed.  
				form.save()
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect("/reservation/%s" % reservation_id)
		else:
			form = get_reservation_form_for_perms(request, post=False, instance=reservation)
			
		return render(request, 'reservation_edit.html', {'form': form, 
			'reservation_id': reservation_id, 'arrive': reservation.arrive,
			'depart': reservation.depart, 'is_house_admin' : is_house_admin,
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
		user = User()
		for field in user._meta.fields:
			if field.name in cleaned_data:
				setattr(user, field.name, cleaned_data[field.name])
		# the password has been validated by the form
		user.set_password(cleaned_data['password2'])
		user.save()

		profile = UserProfile(user=user)
		for field in profile._meta.fields:
			if field.name in cleaned_data:
				setattr(profile, field.name, cleaned_data[field.name])
		profile.save()

		new_user = authenticate(username=user.username, password=cleaned_data['password2'])
		login(request, new_user)
		signals.user_activated.send(sender=self.__class__, user=new_user, request=request)
		return new_user

	def activate(self, request, user):
		# we're not using the registration system's activation features ATM.
		return True


	def registration_allowed(self, request):
		if request.user.is_authenticated():
			return False
		else: return True

	def post_registration_redirect(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		account activation. 

		We're not using the registration system's activation features ATM, so
		interrupt the registration process here.
		"""
		url_path = request.get_full_path().split("next=")
		messages.add_message(request, messages.INFO, 'Your account has been created.')
		if url_path[1] == "/reservation/create/":
			return (url_path[1], (), {'username' : user.username})
		else:
			return ('user_details', (), {'username': user.username})


#def Dashboard(request):


