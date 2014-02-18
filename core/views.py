from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import transaction
from PIL import Image
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration import signals
import registration
from core.forms import ReservationForm, UserProfileForm, EmailTemplateForm, MessageCurrentPeopleForm
from django.core.mail import send_mail
from django.core import urlresolvers
import datetime
from django.contrib import messages
from django.conf import settings
from django.utils import simplejson
from core.decorators import group_required
from django.db.models import Q
from core.models import UserProfile, Reservation, Room, Reconcile, EmailTemplate
from core.tasks import send_guest_welcome
import stripe
import uuid, base64, os
from django.core.files import File
from django.core.mail import EmailMultiAlternatives


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
		"past_reservations": past_reservations, "upcoming_reservations": upcoming_reservations, 
		"stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY})

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
def CheckRoomAvailability(request):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	arrive_str = request.POST.get('arrive')
	depart_str = request.POST.get('depart')
	a_month, a_day, a_year = arrive_str.split("/")
	d_month, d_day, d_year = depart_str.split("/")
	arrive = datetime.date(int(a_year), int(a_month), int(a_day))
	depart = datetime.date(int(d_year), int(d_month), int(d_day))
	avail_by_room = Room.objects.availability(arrive, depart)
	# all rooms should have an associated list of the same length that covers
	# all days, so just grab the dates from any one of them (they are already
	# sorted).
	per_date_avail = avail_by_room[avail_by_room.keys()[0]]
	dates = [tup[0] for tup in per_date_avail]
	nights = (depart - arrive).days
	free_rooms = Room.objects.free(arrive, depart)	
	# add some info to free_rooms:
	for room in free_rooms:
		room.value = nights*room.default_rate
	return render(request, "snippets/availability_calendar.html", {"avail": avail_by_room, "dates": dates, 
		'free_rooms': free_rooms, 'nights': nights, })


@login_required
def ReservationSubmit(request):
	if request.method == 'POST':
		print request.POST
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

	# pass the rate for each room to the template so we can update the cost of
	# a reservation in real time. 
	rooms = Room.objects.all()
	room_list = {}
	for room in rooms:
		room_list[room.name] = room.default_rate
	room_list = simplejson.dumps(room_list)
	return render(request, 'reservation.html', {'form': form, 'is_house_admin': is_house_admin, 
		"room_list": room_list, 'max_days': settings.MAX_RESERVATION_DAYS })


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
		if reservation.arrive >= datetime.date.today():
			past = False
		else:
			past = True
		if reservation.reconcile.status == Reconcile.PAID:
			paid = True
		else:
			paid = False
		return render(request, "reservation_detail.html", {"reservation": reservation, "past":past, 
			"stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY, "paid": paid, "contact" : settings.DEFAULT_FROM_EMAIL})

@login_required
def UserEdit(request, username):
	profile = UserProfile.objects.get(user__username=username)
	user = User.objects.get(username=username)
	if request.user.is_authenticated() and request.user.id == user.id:
		if request.method == "POST":
			profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
			if profile_form.is_valid(): 
				updated_user = profile_form.save()
				profile = updated_user.profile

				print "request data: image field"
				img_data = request.POST.get("image")
				if img_data:
					print img_data
					img_data = base64.b64decode(img_data)
					filename = "%s.png" % uuid.uuid4()
					# XXX make the upload path a fixed setting in models, since it's
					# referenced in three places
					upload_path = "data/avatars/%s/" % user.username
					upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
					if not os.path.exists(upload_abs_path):
						os.makedirs(upload_abs_path)
					full_file_name = os.path.join(upload_abs_path, filename)
					with open(full_file_name, 'wb') as f:
						f.write(img_data)
						f.close()
					profile.image = full_file_name

				profile.save()
				client_msg = "Your profile has been updated."
				messages.add_message(request, messages.INFO, client_msg)
				return HttpResponseRedirect("/people/%s" % updated_user.username)
			else:
				print profile_form.errors
		else:
			if profile.image:
				image_required = False
			else:
				image_required = True
			print 'profile image required?'
			print image_required
			profile_form = UserProfileForm(instance=profile)		
		return render(request, 'registration/registration_form.html', {'form': profile_form, 'image_required': image_required, 'existing_user': True})
	return HttpResponseRedirect("/")

@login_required
def UserAddCard(request, username):
	''' Adds a card from either the reservation page or the user profile page.
	Displays success or error message and returns user to originating page.'''

	user = User.objects.get(username=username)
	if not request.method == 'POST' or request.user != user:
		return HttpResponseRedirect('/404')

	token = request.POST.get('stripeToken')
	if not token:
		messages.add_message(request, messages.INFO, "No credit card information was given.")
		return HttpResponseRedirect("/people/%s" % username)

	reservation_id = request.POST.get('res-id')
	if reservation_id:
		reservation = Reservation.objects.get(id=reservation_id)

	stripe.api_key = settings.STRIPE_SECRET_KEY

	try:
		customer = stripe.Customer.create(
			card=token,
			description=user.email
		)
		profile = user.profile
		profile.customer_id = customer.id
		profile.save()

		# if the card is being added from the reservation page, then charge the card
		if reservation_id:
			try:
				# charges card, saves payment details and emails a receipt to
				# the user
				reservation.reconcile.charge_card()
				reservation.status = Reservation.CONFIRMED
				reservation.save()
				days_until_arrival = (reservation.arrive - datetime.date.today()).days
				if days_until_arrival < settings.WELCOME_EMAIL_DAYS_AHEAD:
					send_guest_welcome([reservation,])
				messages.add_message(request, messages.INFO, 'Thank you! Your payment has been processed and a receipt emailed to you at %s. You will receive an email with house access information and other details %d days before your arrival.' % (user.email, settings.WELCOME_EMAIL_DAYS_AHEAD))
				return HttpResponseRedirect("/reservation/%d" % int(reservation_id))
			except stripe.CardError, e:
				raise stripe.CardError(e)
		# if the card is being added from the user profile page, just save it. 
		else:
			messages.add_message(request, messages.INFO, 'Thanks! Your card has been saved.')
			return HttpResponseRedirect("/people/%s" % username)
	except stripe.CardError, e:
		messages.add_message(request, messages.ERROR, 'Drat, it looks like there was a problem with your card: <em>%s</em>. Please try again.' % (e))
		if reservation_id:
			return HttpResponseRedirect("/reservation/%d" % int(reservation_id))
		else:
			return HttpResponseRedirect("/people/%s" % username)

def UserDeleteCard(request, username):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	profile = UserProfile.objects.get(user__username=username)
	profile.customer_id = None
	profile.save()
	
	messages.add_message(request, messages.INFO, "Card deleted.")
	return HttpResponseRedirect("/people/%s" % profile.user.username)



@login_required
def ReservationEdit(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	# need to pull these dates out before we pass the instance into
	# the ReservationForm, since it (apparently) updates the instance 
	# immediately (which is weird, since it hasn't validated the form 
	# yet!)
	original_arrive = reservation.arrive
	original_depart = reservation.depart
	original_room = reservation.room
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
				# still pending to begin with, notify an admin and go back to
				# pending (unless it's hosted, then we don't generate an
				# email).
				if not reservation.hosted and (reservation.status != 'pending' and 
					(reservation.arrive != original_arrive or reservation.depart != original_depart or reservation.room != original_room )):

					print "reservation room or date was changed. updating status."
					reservation.status = "pending"
					
					# notify house_admins by email
					house_admins = User.objects.filter(groups__name='house_admin')
					subject = "[Embassy SF] Reservation Updated, %s %s, %s - %s" % (reservation.user.first_name, 
						reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
					sender = "stay@embassynetwork.com"
					domain = Site.objects.get_current().domain
					admin_path = urlresolvers.reverse('reservation_manage', args=(reservation.id,))
					text = '''Howdy, 

A reservation has been updated and requires your review. 

You can view, approve or deny this request at %s%s.''' % (domain, admin_path)
					# XXX TODO this is terrible. should have an alias and let a mail agent handle this!
					for admin in house_admins:
						recipient = [admin.email,]
						send_mail(subject, text, sender, recipient) 

					client_msg = 'The reservation was updated and the new information will be reviewed for availability.'
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
	if not (request.user.is_authenticated() and request.user == reservation.user 
		and request.method == "POST" and reservation.status == 'approved'):
		return HttpResponseRedirect("/")

	if not reservation.user.profile.customer_id:
		messages.add_message(request, messages.INFO, 'Please enter payment information to confirm your reservation.')
	else:
		try:
			reservation.reconcile.charge_card()
			reservation.status = Reservation.CONFIRMED
			reservation.save()
			# if reservation start date is sooner than WELCOME_EMAIL_DAYS_AHEAD,
			# need to send them house info manually. 
			days_until_arrival = (reservation.arrive - datetime.date.today()).days
			if days_until_arrival < settings.WELCOME_EMAIL_DAYS_AHEAD:
				send_guest_welcome([reservation,])
			messages.add_message(request, messages.INFO, 'Thank you! Your payment has been received and a receipt emailed to you at %s' % reservation.user.email)
		except stripe.CardError, e:
			messages.add_message(request, messages.ERROR, 'Drat, it looks like there was a problem with your card: <em>%s</em>. Please try again.' % (e))

	return HttpResponseRedirect("/reservation/%s" % reservation_id)


@login_required
def ReservationCancel(request, reservation_id):
	if not request.method == "POST":
		return HttpResponseRedirect("/404")

	reservation = Reservation.objects.get(id=reservation_id)
	if (not (request.user.is_authenticated() and request.user == reservation.user) 
			and not request.user.groups.filter(name='house_admin')):
		return HttpResponseRedirect("/404")

	redirect = request.POST.get("redirect")

	reservation.cancel()
	messages.add_message(request, messages.INFO, 'The reservation has been canceled.')
	username = reservation.user.username
	return HttpResponseRedirect(redirect)


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

@login_required
def PeopleDaterangeQuery(request):

	start_str = request.POST.get('start_date')
	end_str = request.POST.get('end_date')
	s_month, s_day, s_year = start_str.split("/")
	e_month, e_day, e_year = end_str.split("/")
	start_date = datetime.date(int(s_year), int(s_month), int(s_day))
	end_date = datetime.date(int(e_year), int(e_month), int(e_day))
	reservations_for_daterange = Reservation.objects.filter(Q(status="confirmed")).exclude(depart__lt=start_date).exclude(arrive__gte=end_date)
	recipients = []
	for r in reservations_for_daterange:
		recipients.append(r.user)
	residents = User.objects.filter(groups__name='residents')
	recipients = recipients + list(residents)
	html = "<div class='btn btn-info disabled' id='recipient-list'>Your message will go to these people: "
	for person in recipients:
		info = "<a class='link-light-color' href='/people/" + person.username + "'>" + person.first_name + " " + person.last_name + "</a>, "
		html += info;

	html = html.strip(", ")
	html += "</div>"
	return HttpResponse(html)
	

@login_required
def broadcast(request):
	# the user must be authenticated because we have the @login_required
	# decorator. 
	sender = request.user 
	print 'sender is ' + sender.username
	if request.method == 'POST':
		form = MessageCurrentPeopleForm(request.POST, sender=sender)
		if form.is_valid():
			# get current people for the specified dates (residents + guests)
			# this is a waste since we already ueried the DB for the list of
			# users when the dates were selected. ideally should pass along
			# this info instead of re-querying. 
			start_str = request.POST.get('start_date')
			end_str = request.POST.get('end_date')
			s_month, s_day, s_year = start_str.split("/")
			e_month, e_day, e_year = end_str.split("/")
			start_date = datetime.date(int(s_year), int(s_month), int(s_day))
			end_date = datetime.date(int(e_year), int(e_month), int(e_day))

			reservations_for_daterange = Reservation.objects.filter(Q(status="confirmed")).exclude(depart__lt=start_date).exclude(arrive__gte=end_date)

			# Send email
			recipients = []
			for r in reservations_for_daterange:
				recipients.append(r.user.email)
			residents = User.objects.filter(groups__name='residents')
			residents = list(residents)
			for r in residents:
				recipients.append(r.email)
			text_content = request.POST.get('body') + "\n\n" + request.POST.get('footer')
			subject = request.POST.get('subject') 
			sender = sender.email
			msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
			msg.send()
			messages.add_message(request, messages.INFO, 'Your message has been sent!')
			return HttpResponseRedirect('/broadcast')

		else:
			print "form not valid"
			print form.errors


	else:
		form = MessageCurrentPeopleForm(sender=sender)		
	return render(request, "broadcast.html", {"form": form})

# ******************************************************
#           reservation management views
# ******************************************************

@group_required('house_admin')
def ReservationList(request):
	reservations = Reservation.objects.all()
	pending = Reservation.objects.filter(status="pending")
	approved = Reservation.objects.filter(status="approved")
	confirmed = Reservation.objects.filter(status="confirmed")
	canceled = Reservation.objects.exclude(status="confirmed").exclude(status="approved").exclude(status="pending")
	return render(request, 'reservation_list.html', {"pending": pending, "approved": approved, 
		"confirmed": confirmed, "canceled": canceled})


@group_required('house_admin')
def ReservationManage(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	user = User.objects.get(username=reservation.user.username)
	other_reservations = Reservation.objects.filter(user=user).exclude(status='deleted').exclude(id=reservation_id)
	past_reservations = []
	upcoming_reservations = []
	for res in other_reservations:
		if res.arrive >= datetime.date.today():
			upcoming_reservations.append(res)
		else:
			past_reservations.append(res)
	domain = Site.objects.get_current().domain
	emails = EmailTemplate.objects.filter(Q(shared=True) | Q(creator=request.user))
	email_forms = []
	email_templates_by_name = []
	for email_template in emails:
		form = EmailTemplateForm(email_template, reservation)
		email_forms.append(form)
		email_templates_by_name.append(email_template.name)
	
	availability = Room.objects.availability(reservation.arrive, reservation.depart)
	free = Room.objects.free(reservation.arrive, reservation.depart)
	per_date_avail = availability[availability.keys()[0]]
	dates = [tup[0] for tup in per_date_avail]
	if reservation.room in free:
		room_has_availability = True
	else:
		room_has_availability = False

	return render(request, 'reservation_manage.html', {
		"r": reservation, 
		"past_reservations":past_reservations, 
		"upcoming_reservations": upcoming_reservations,
		"email_forms" : email_forms,
		"email_templates_by_name" : email_templates_by_name,
		"days_before_welcome_email" : settings.WELCOME_EMAIL_DAYS_AHEAD,
		"room_has_availability" : room_has_availability,
		"avail": availability, "dates": dates,
		"domain": domain
	})


@group_required('house_admin')
def ReservationManageUpdate(request, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	reservation = Reservation.objects.get(id=reservation_id)
	reservation_action = request.POST.get('reservation-action')
	try:
		if reservation_action == 'set-tentative':
			reservation.set_tentative()
		elif reservation_action == 'set-confirm':
			reservation.set_confirmed()
			days_until_arrival = (reservation.arrive - datetime.date.today()).days
			if days_until_arrival < settings.WELCOME_EMAIL_DAYS_AHEAD:
				send_guest_welcome([reservation,])
		elif reservation_action == 'set-comp':
			reservation.set_comp()
		elif reservation_action == 'res-charge-card':
			try:
				reservation.reconcile.charge_card()
				reservation.set_confirmed()
				days_until_arrival = (reservation.arrive - datetime.date.today()).days
				if days_until_arrival < settings.WELCOME_EMAIL_DAYS_AHEAD:
					send_guest_welcome([reservation,])
			except stripe.CardError, e:
				raise Reservation.ResActionError(e)
		else:
			raise Reservation.ResActionError("Unrecognized action.")

		messages.add_message(request, messages.INFO, 'Your action has been registered!')
		status_area_html = render(request, "snippets/res_status_area.html", {"r": reservation})
		return status_area_html

	except Reservation.ResActionError, e:
		messages.add_message(request, messages.INFO, "Error: %s" % e)
		return render(request, "snippets/res_status_area.html", {"r": reservation})

@group_required('house_admin')
def ReservationChargeCard(request, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	reservation = Reservation.objects.get(id=reservation_id)
	try:
		reservation.reconcile.charge_card()
		return HttpResponse()
	except stripe.CardError, e:
		return HttpResponse(status=500)

@group_required('house_admin')
def ReservationSendReceipt(request, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	reservation = Reservation.objects.get(id=reservation_id)
	if reservation.reconcile.status == Reconcile.PAID:
		reservation.reconcile.send_receipt()
	messages.add_message(request, messages.INFO, "The receipt was sent.")
	return HttpResponseRedirect('/manage/reservation/%d' % reservation.id)


@group_required('house_admin')
def ReservationToggleComp(request, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')
	reservation = Reservation.objects.get(id=reservation_id)
	reconcile = reservation.reconcile
	if reconcile.status != Reconcile.COMP:
		reconcile.status = Reconcile.COMP
	else:
		reconcile.status = Reconcile.UNPAID
		# if confirmed set status back to APPROVED 
		if reservation.status == Reservation.CONFIRMED:
			reservation.status = Reconcile.APPROVED
			reservation.save()
	reconcile.save()
	return HttpResponseRedirect('/manage/reservation/%d' % reservation.id)

@group_required('house_admin')
def ReservationSendMail(request, reservation_id):
	if not request.method == 'POST':
		return HttpResponseRedirect('/404')

	print request.POST
	subject = request.POST.get("subject")
	recipient = [request.POST.get("recipient"),]
	sender = request.POST.get("sender")
	body = request.POST.get("body") + "\n\n" + request.POST.get("footer")
	send_mail(subject, body, sender, recipient)

	reservation = Reservation.objects.get(id=reservation_id)
	reservation.mark_last_msg() 

	messages.add_message(request, messages.INFO, "Your message was sent.")
	return HttpResponseRedirect('/manage/reservation/%s' % reservation_id)

# ******************************************************
#           registration callbacks and views
# ******************************************************


'''A registration backend that supports capturing user profile
information during registration.'''

	
class Registration(registration.views.RegistrationView):
	
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

		print "request data: image field"
		img_data = request.POST.get("image")
		# If none or len 0, means illegal image data
		if img_data == None or len(img_data) == 0:
			pass

		# Decode the image data
		img_data = base64.b64decode(img_data)
		filename = "%s.png" % uuid.uuid4()

		# XXX make the upload path a fixed setting in models, since it's
		# reference in three places
		upload_path = "data/avatars/%s/" % user.username
		upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
		if not os.path.exists(upload_abs_path):
			os.makedirs(upload_abs_path)
		full_file_name = os.path.join(upload_abs_path, filename)

		with open(full_file_name, 'wb') as f:
			f.write(img_data)
			f.close()

		profile.image = full_file_name
		profile.save()

		new_user = authenticate(username=user.username, password=cleaned_data['password2'])
		login(request, new_user)
		signals.user_activated.send(sender=self.__class__, user=new_user, request=request)
		return new_user

	def registration_allowed(self, request):
		if request.user.is_authenticated():
			return False
		else: return True

	def get_success_url(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		account activation. 

		We're not using the registration system's activation features ATM, so
		interrupt the registration process here.
		"""
		url_path = request.get_full_path().split("next=")
		messages.add_message(request, messages.INFO, 'Your account has been created. Now it is time to make a reservation!')
		if len(url_path) > 1 and url_path[1] == "/reservation/create/":
			return (url_path[1], (), {'username' : user.username})
		else:
			return ('user_details', (), {'username': user.username})

class Activation(registration.views.ActivationView):
	def activate(self, request, user):
		# we're not using the registration system's activation features ATM.
		return True




