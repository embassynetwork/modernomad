from django.contrib.auth.models import User
from django.core import urlresolvers
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import Site
from models import get_location, Reservation
from django.http import HttpResponse, HttpResponseRedirect
from gather.tasks import published_events_today_local, events_pending
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import requests
import datetime
import logging

logger = logging.getLogger(__name__)

weekday_number_to_name = {
	0: "Monday",
	1: "Tuesday",
	2: "Wednesday",
	3: "Thursday",
	4: "Friday",
	5: "Saturday",
	6: "Sunday"
}

def mailgun_send(mailgun_data):
	logger.debug("Mailgun send: %s" % mailgun_data)
	if settings.DEBUG:
		# When this is true you will see this message in the mailgun logs but
		# nothing will actually be delivered
		mailgun_data["o:testmode"] = "yes"
	resp = requests.post("https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
		auth=("api", settings.MAILGUN_API_KEY),
		data=mailgun_data
	)
	logger.debug("Mailgun response: %s" % resp.text)
	return HttpResponse(status=200)

@csrf_exempt
def current(request, location_slug):
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		print 'location not found'
		return HttpResponse(status=200)
	logger.debug('current@ for location: %s' % location)

	# we think that message_headers is a list of strings
	message_headers = json.loads(request.POST.get('message-headers'))
	message_header_keys = [item[0] for item in message_headers]

	# make sure this isn't an email we have already forwarded (cf. emailbombgate 2014)
	# A List-Id header will only be present if it has been added manually in
	# this function, ie, if we have already processed this message. 
	if request.POST.get('List-Id') or 'List-Id' in message_header_keys:
		# mailgun requires a code 200 or it will continue to retry delivery
		logger.debug('List-Id header was found! Dropping message silently')
		return HttpResponse(status=200)

	#if 'Auto-Submitted' in message_headers or message_headers['Auto-Submitted'] != 'no':
	if 'Auto-Submitted' in message_header_keys: 
		logger.info('message appears to be auto-submitted. reject silently')
		return HttpResponse(status=200)

	recipient = request.POST.get('recipient')
	from_address = request.POST.get('from')
	logger.debug('from: %s' % from_address)
	sender = request.POST.get('sender')
	logger.debug('sender: %s' % sender)
	subject = request.POST.get('subject')
	body_plain = request.POST.get('body-plain')
	body_html = request.POST.get('body-html')

	# Add any current reservations
	current_emails = [] 
	for r in Reservation.today.confirmed(location):
		current_emails.append(r.user.email)

	# Add all the residents at this location
	for r in location.residents.all():
		current_emails.append(r.email)
		
	# Add the house admins
	for a in location.house_admins.all():
		current_emails.append(a.email)

	# TODO? make sure the sender is on the list?
	#if not sender in current_emails:
		# Do something about it
		# Bounce? Moderate?

	# Now loop through all the emails and build the bcc list we will use.
	# This makes sure there are no duplicate emails.
	bcc_list = []
	for email in current_emails:
		if email not in bcc_list:
			bcc_list.append(email)
	logger.debug("bcc list: %s" % bcc_list)
	
	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] [Current Guests and Residents] " 
		subject = prefix + subject
	logger.debug("subject: %s" % subject)

	# add in footer
	text_footer = '''\n\n-------------------------------------------\nYou are receving this email because you are a current guest or resident at %s. This list is used to share questions, ideas and activities with others currently at this location. Feel free to respond.'''% location.name
	html_footer = '''<br><br>-------------------------------------------<br>You are receving this email because you are a current guest or resident at %s. This list is used to share questions, ideas and activities with others currently at this location. Feel free to respond.'''% location.name
	body_plain = body_plain + footer
	body_html = body_html + footer

	# send the message 
	list_address = "current@%s.%s" % (location.slug, settings.LIST_DOMAIN)
	mailgun_data =  {"from": from_address,
		"to": [recipient, ],
		"bcc": bcc_list,
		"subject": subject,
		"text": body_plain,
		"html": body_html,
		# attach some headers: LIST-ID, REPLY-TO, MSG-ID, precedence...
		# Precedence: list - helps some out of office auto responders know not to send their auto-replies. 
		"h:List-Id": list_address,
		"h:Precedence": "list",
		# Reply-To: list email apparently has some religious debates
		# (http://www.gnu.org/software/mailman/mailman-admin/node11.html) but seems
		# to be common these days 
		"h:Reply-To": list_address,
	}
	return mailgun_send(mailgun_data)

@csrf_exempt
def stay(request, location_slug):
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		return HttpResponse(status=200)
	logger.debug('stay@ for location: %s' % location)

	# we think that message_headers is a list of strings
	message_headers = json.loads(request.POST.get('message-headers'))
	message_header_keys = [item[0] for item in message_headers]

	# make sure this isn't an email we have already forwarded (cf. emailbombgate 2014)
	# A List-Id header will only be present if it has been added manually in
	# this function, ie, if we have already processed this message. 
	if request.POST.get('List-Id') or 'List-Id' in message_header_keys:
		# mailgun requires a code 200 or it will continue to retry delivery
		logger.debug('List-Id header was found! Dropping message silently')
		return HttpResponse(status=200)

	#if 'Auto-Submitted' in message_headers or message_headers['Auto-Submitted'] != 'no':
	if 'Auto-Submitted' in message_header_keys: 
		logger.info('message appears to be auto-submitted. reject silently')
		return HttpResponse(status=200)

	recipient = request.POST.get('recipient')
	from_address = request.POST.get('from')
	logger.debug('from: %s' % from_address)
	sender = request.POST.get('sender')
	logger.debug('sender: %s' % sender)	
	subject = request.POST.get('subject')
	body_plain = request.POST.get('body-plain')
	body_html = request.POST.get('body-html')

	# retrieve the current house admins for this location
	location_admins = location.house_admins.all()
	bcc_list = []
	for person in location_admins:
		if person.email not in bcc_list:
			bcc_list.append(person.email)
	logger.debug("bcc list: %s" % bcc_list)

	# TODO? make sure the sender is on the list?
	#if not sender in current_emails:
		# Do something about it
		# Bounce? Moderate?

	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] [Admin] " 
		subject = prefix + subject
	logger.debug("subject: %s" % subject)

	# add in footer
	text_footer = '''\n\n-------------------------------------------\nYou are receving email to %s because you are a location admin at %s. Send mail to this list to reach other admins.''' % (recipient, location.name)
	html_footer = '''<br><br>-------------------------------------------<br>You are receving email to %s because you are a location admin at %s. Send mail to this list to reach other admins.''' % (recipient, location.name)
	body_plain = body_plain + text_footer
	body_html = body_html + html_footer

	# send the message 
	list_address = location.from_email()
	mailgun_data = {"from": from_address,
			"to": [recipient, ],
			"bcc": bcc_list,
			"subject": subject,
			"text": body_plain,
			"html": body_html,
			# attach some headers: LIST-ID, REPLY-TO, MSG-ID, precedence...
			# Precedence: list - helps some out of office auto responders know not to send their auto-replies. 
			"h:List-Id": list_address,
			"h:Precedence": "list",
			# Reply-To: list email apparently has some religious debates
			# (http://www.gnu.org/software/mailman/mailman-admin/node11.html) but seems
			# to be common these days 
			"h:Reply-To": list_address
		}
	return mailgun_send(mailgun_data)

def send_from_location_address(subject, text_content, html_content, recipient, location):
	''' a somewhat generic send function using mailgun that sends plaintext
	from the location's generic stay@ address.'''
	location_address = location.from_email()
	if not html_content:
		html_content = text_content
	mailgun_data={"from": location_address,
		"to": [recipient, ],
		"subject": subject,
		"text": text_content,
		"html": html_content,
	}
	return mailgun_send(mailgun_data)

def send_receipt(reservation):
	location = reservation.location

	plaintext = get_template('emails/receipt.txt')
	htmltext = get_template('emails/receipt.html')
	c = Context({
		'today': timezone.localtime(timezone.now()), 
		'user': reservation.user, 
		'location': reservation.location,
		'reservation': reservation,
		}) 

	subject = "[%s] Receipt for your Stay %s - %s" % (location.email_subject_prefix, str(reservation.arrive), str(reservation.depart))  
	sender = location.from_email()
	recipient = [reservation.user.email,]
	text_content = plaintext.render(c)
	html_content = htmltext.render(c)
	return send_from_location_address(subject, text_content, html_context, recipient, location)

def send_invoice(reservation):
	''' trigger a reminder email to the guest about payment.''' 
	if reservation.is_comped():
		# XXX TODO eventually send an email for COMPs too, but a
		# different once, with thanks/asking for feedback.
		return

	plaintext = get_template('emails/invoice.txt')
	htmltext = get_template('emails/invoice.html')
	c = Context({
		'today': timezone.localtime(timezone.now()), 
		'user': reservation.user, 
		'location': reservation.location,
		'reservation': reservation,
		}) 

	subject = "[%s] Thanks for Staying with us!" % reservation.location.email_subject_prefix 
	recipient = [reservation.user.email,]
	text_content = plaintext.render(c)
	html_content = htmltext.render(c)
	return send_from_location_address(subject, text_content, html_context, recipient, reservation.location)

def new_reservation_notify(reservation):
	house_admins = reservation.location.house_admins.all()
	domain = Site.objects.get_current().domain

	subject = "[%s] Reservation Request, %s %s, %s - %s" % (reservation.location.email_subject_prefix, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	sender = reservation.location.from_email()
	recipients = []
	for admin in house_admins:
		recipients.append(admin.email)

	plaintext = get_template('emails/newreservation.txt')
	htmltext = get_template('emails/newreservation.html')
	c = Context({
		'location': reservation.location.name,
		'status': reservation.status, 
		'user_image' : "https://" + domain+"/media/"+ str(reservation.user.profile.image_thumb),
		'first_name': reservation.user.first_name, 
		'last_name' : reservation.user.last_name, 
		'room_name' : reservation.room.name, 
		'arrive' : str(reservation.arrive), 
		'depart' : str(reservation.depart), 
		'purpose': reservation.purpose, 
		'comments' : reservation.comments, 
		'bio' : reservation.user.profile.bio,
		'referral' : reservation.user.profile.referral, 
		'projects' : reservation.user.profile.projects, 
		'sharing': reservation.user.profile.sharing, 
		'discussion' : reservation.user.profile.discussion, 
		"admin_url" : "https://" + domain + urlresolvers.reverse('reservation_manage', args=(reservation.location.slug, reservation.id,))
	})
	text_content = plaintext.render(c)
	html_content = htmltext.render(c)

	return send_from_location_address(subject, text_content, html_context, recipient, reservation.location)

def updated_reservation_notify(reservation):
	domain = Site.objects.get_current().domain
	admin_path = urlresolvers.reverse('reservation_manage', args=(reservation.location.slug, reservation.id,))
	text_content = '''Howdy,\n\nA reservation has been updated and requires your review.\n\nYou can view, approve or deny this request at %s%s.''' % (domain, admin_path)
	recipients = []
	for admin in reservation.location.house_admins.all():
		recipients.append(admin.email)
	subject = "[%s] Reservation Updated, %s %s, %s - %s" % (location.email_subject_prefix, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	mailgun_data={"from": location.from_email(),
		"to": recipients,
		"subject": subject,
		"text": text_content,
	}
	return mailgun_send(mailgun_data)

def guest_daily_update(location):
	# this is split out by location because each location has a timezone that affects the value of 'today'
	today = timezone.localtime(timezone.now())
	arriving_today = Reservation.objects.filter(location=location).filter(arrive=today).filter(status='confirmed')
	departing_today = Reservation.objects.filter(location=location).filter(depart=today).filter(status='confirmed')
	domain = Site.objects.get_current().domain
	events=_today = published_events_today_local(location=location)

	plaintext = get_template('emails/guest_daily_update.txt')
	c = Context({
		'arriving' : arriving_today,
		'departing' : departing_today,
		'domain': domain,
		'events_today': events_today,
		'location_name': location.name,
	})
	text_content = plaintext.render(c)
	
	# who should we tell?
	reservations_here_today = Reservation.today.confirmed(location)
	guest_emails = []
	for r in reservations_here_today:
		guest_emails.append(r.user.email)
	
	mailgun_data={
		"from": location.from_email(),
		"to": guest_emails,
		"subject": "[%s] Events, Arrivals and Departures for %s" % (location.email_subject_prefix, str(today)),
		"text": text_content,
	}
	return mailgun_send(mailgun_data)

def admin_daily_update(location):
	# this is split out by location because each location has a timezone that affects the value of 'today'
	today = timezone.localtime(timezone.now())
	arriving_today = Reservation.objects.filter(location=location).filter(arrive=today).filter(status='confirmed')
	departing_today = Reservation.objects.filter(location=location).filter(depart=today).filter(status='confirmed')
	domain = Site.objects.get_current().domain
	events_today = published_events_today_local(location=location)
	pending_or_feedback = events_pending(location=location)
	
	plaintext = get_template('emails/admin_daily_update.txt')
	c = Context({
		'arriving' : arriving_today,
		'departing' : departing_today,
		'domain': domain,
		'location_name': location.name,
		'events_today': events_today,
		'events_pending': pending_or_feedback['pending'],
		'events_feedback': pending_or_feedback['feedback'],
	})
	text_content = plaintext.render(c)
	
	admins_emails = []
	for admin in location.house_admins.all():
		admins_emails.append(admin.email)

	mailgun_data={"from": location.from_email(),
		"to": admins_emails,
		"subject": "[%s] %s Events and Guests" % (location.email_subject_prefix, str(today)),
		"text": text_content,
	}
	return mailgun_send(mailgun_data)

def guest_welcome(reservation):
	''' Send guest a welcome email'''
	# this is split out by location because each location has a timezone that affects the value of 'today'
	domain = Site.objects.get_current().domain
	plaintext = get_template('emails/pre_arrival_welcome.txt')
	day_of_week = weekday_number_to_name[reservation.arrive.weekday()]
	c = Context({
		'first_name': reservation.user.first_name,
		'day_of_week' : day_of_week,
		'site_url': urlresolvers.reverse('location_home', args=(reservation.location.slug,)),
		'house_code': reservation.location.house_access_code,
		'location_name': reservation.location.name,
		'address': reservation.location.address,
		'ssid': reservation.location.ssid,
		'ssid_password': reservation.location.ssid_password,
		'events_url' : domain + '/events/upcoming/',
		'current_email' : 'current@%s.mail.embassynetwork.com' % reservation.location.slug,
		'profile_url' : "https://" + domain + urlresolvers.reverse('user_detail', args=(reservation.user.username,)),
		'reservation_url' : "https://" + domain + urlresolvers.reverse('reservation_detail', args=(reservation.location.slug, reservation.id,)),
	})
	text_content = plaintext.render(c)
	mailgun_data={
			"from": reservation.location.from_email(),
			"to": [reservation.user.email,],
			"subject": "[%s] See you on %s" % (reservation.location.email_subject_prefix, day_of_week),
			"text": text_content,
		}
	return mailgun_send(mailgun_data)
