from django.contrib.auth.models import User
from django.core import urlresolvers
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Template, TemplateDoesNotExist, Context
from django.contrib.sites.models import Site
from models import get_location, Reservation, LocationEmailTemplate
from django.http import HttpResponse, HttpResponseRedirect
from gather.tasks import published_events_today_local, events_pending
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from core.models import Reservation
from gather.models import Event
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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

def mailgun_send(mailgun_data, files_dict=None):
	logger.debug("Mailgun send: %s" % mailgun_data)
	logger.debug("Mailgun files: %s" % files_dict)
	if settings.DEBUG:
		if not hasattr(settings, 'MAILGUN_DEBUG') or settings.MAILGUN_DEBUG:
			# We will see this message in the mailgun logs but nothing will actually be delivered
			logger.debug("mailgun_send: setting testmode=yes")
			mailgun_data["o:testmode"] = "yes"
	resp = requests.post("https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
		auth=("api", settings.MAILGUN_API_KEY),
		data=mailgun_data, 
		files=files_dict
	)
	logger.debug("Mailgun response: %s" % resp.text)
	return HttpResponse(status=200)

def send_from_location_address(subject, text_content, html_content, recipient, location):
	''' a somewhat generic send function using mailgun that sends plaintext
	from the location's generic stay@ address.'''
	mailgun_data={"from": location.from_email(),
		"to": [recipient, ],
		"subject": subject,
		"text": text_content,
	}
	if html_content:
		mailgun_data["html"] = html_content
	return mailgun_send(mailgun_data)

def get_templates(location, email_key):
	text_template = None
	html_template = None

	template_override = LocationEmailTemplate.objects.filter(location=location, key=email_key)
	if template_override and template_override.count() > 0:
		t = template_override[0]
		if t.text_body:
			text_template = Template(t.text_body)
		if t.html_body:
			html_template = Template(t.html_body)
	else:
		try:
			text_template = get_template("emails/%s.txt" % email_key)
			html_template = get_template("emails/%s.html" % email_key)
		except TemplateDoesNotExist:
			pass

	return (text_template, html_template)

def render_templates(context, location, email_key):
	text_content = None
	html_content = None
	
	text_template, html_template = get_templates(location, email_key)

	if text_template:
		text_content = text_template.render(context)
	if html_template:
		html_content = html_template.render(context)
	
	return (text_content, html_content)

############################################
#            RESERVATION EMAILS            #
############################################

def send_receipt(reservation):
	location = reservation.location
	subject = "[%s] Receipt for your Stay %s - %s" % (location.email_subject_prefix, str(reservation.arrive), str(reservation.depart))
	recipient = [reservation.user.email,]
	c = Context({
		'today': timezone.localtime(timezone.now()), 
		'user': reservation.user, 
		'location': location,
		'reservation': reservation,
		})
	text_content, html_content = render_templates(c, location, LocationEmailTemplate.RECEIPT)
	return send_from_location_address(subject, text_content, html_content, recipient, location)

def send_invoice(reservation):
	''' trigger a reminder email to the guest about payment.''' 
	if reservation.is_comped():
		return send_comp_invoice(reservation)

	location = reservation.location
	subject = "[%s] Thanks for Staying with us!" % location.email_subject_prefix 
	recipient = [reservation.user.email,]
	c = Context({
		'today': timezone.localtime(timezone.now()), 
		'user': reservation.user, 
		'location': location,
		'reservation': reservation,
		'domain': Site.objects.get_current().domain,
		}) 
	text_content, html_content = render_templates(c, location, LocationEmailTemplate.INVOICE)
	return send_from_location_address(subject, text_content, html_content, recipient, location)

def send_comp_invoice(reservation):
	# XXX TODO eventually send an email for COMPs too, but a
	# different once, with thanks/asking for feedback.
	return

def new_reservation_notify(reservation):
	house_admins = reservation.location.house_admins.all()
	domain = Site.objects.get_current().domain
	location = reservation.location

	subject = "[%s] Reservation Request, %s %s, %s - %s" % (location.email_subject_prefix, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	sender = location.from_email()
	recipients = []
	for admin in house_admins:
		recipients.append(admin.email)

	c = Context({
		'location': location.name,
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
		"admin_url" : "https://" + domain + urlresolvers.reverse('reservation_manage', args=(location.slug, reservation.id,))
	})
	text_content, html_content = render_templates(c, location, LocationEmailTemplate.NEW_RESERVATION)

	return send_from_location_address(subject, text_content, html_content, recipients, reservation.location)

def updated_reservation_notify(reservation):
	domain = Site.objects.get_current().domain
	admin_path = urlresolvers.reverse('reservation_manage', args=(reservation.location.slug, reservation.id,))
	text_content = '''Howdy,\n\nA reservation has been updated and requires your review.\n\nYou can view, approve or deny this request at %s%s.''' % (domain, admin_path)
	recipients = []
	for admin in reservation.location.house_admins.all():
		if not admin.email in recipients:
			recipients.append(admin.email)
	subject = "[%s] Reservation Updated, %s %s, %s - %s" % (reservation.location.email_subject_prefix, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	mailgun_data={"from": reservation.location.from_email(),
		"to": recipients,
		"subject": subject,
		"text": text_content,
	}
	return mailgun_send(mailgun_data)

def guest_welcome(reservation):
	''' Send guest a welcome email'''
	# this is split out by location because each location has a timezone that affects the value of 'today'
	domain = Site.objects.get_current().domain
	location = reservation.location
	intersecting_reservations = Reservation.objects.filter(arrive__gte=reservation.arrive).filter(depart__lte=reservation.depart)
	residents = location.residents.all()
	intersecting_events = Event.objects.filter(location=location).filter(start__gte=reservation.arrive).filter(end__lte=reservation.depart)
	profiles = None
	day_of_week = weekday_number_to_name[reservation.arrive.weekday()]
	
	c = Context({
		'first_name': reservation.user.first_name,
		'day_of_week' : day_of_week,
		'location': reservation.location,
		'current_email' : 'current@%s.mail.embassynetwork.com' % location.slug,
		'site_url': "https://" + domain + urlresolvers.reverse('location_home', args=(location.slug,)),
		'events_url' : "https://" + domain + urlresolvers.reverse('gather_upcoming_events', args=(location.slug,)),
		'profile_url' : "https://" + domain + urlresolvers.reverse('user_detail', args=(reservation.user.username,)),
		'reservation_url' : "https://" + domain + urlresolvers.reverse('reservation_detail', args=(location.slug, reservation.id,)),
		'intersecting_reservations': intersecting_reservations,
		'intersecting_events': intersecting_events,
		'residents': residents,
	})
	text_content, html_content = render_templates(c, location, LocationEmailTemplate.WELCOME)
	
	mailgun_data={
			"from": reservation.location.from_email(),
			"to": [reservation.user.email,],
			"subject": "[%s] See you on %s" % (reservation.location.email_subject_prefix, day_of_week),
			"text": text_content,
		}
	if html_content:
		mailgun_data["html"] = html_content
	
	return mailgun_send(mailgun_data)

############################################
#             LOCATION EMAILS              #
############################################

def guests_residents_daily_update(location):
	# this is split out by location because each location has a timezone that affects the value of 'today'
	today = timezone.localtime(timezone.now())
	arriving_today = Reservation.objects.filter(location=location).filter(arrive=today).filter(status='confirmed')
	departing_today = Reservation.objects.filter(location=location).filter(depart=today).filter(status='confirmed')
	events_today = published_events_today_local(location=location)

	if not arriving_today and not departing_today and not events_today:
		logger.debug("Nothing happening today at %s, skipping daily email" % location.name)
		return

	subject = "[%s] Events, Arrivals and Departures for %s" % (location.email_subject_prefix, str(today.date()))
	
	admin_emails = []
	for admin in location.house_admins.all():
		if not admin.email in admin_emails:
			admin_emails.append(admin.email)
	
	print admin_emails

	to_emails = []
	for r in Reservation.objects.confirmed_on_date(today, location):
		if (not r.user.email in admin_emails) and (not r.user.email in to_emails):
			to_emails.append(r.user.email)

	# Add all the non-admin residents at this location (admins get a different
	# email)
	for r in location.residents.all():
		if (not r.email in admin_emails) and (not r.email in to_emails):
			to_emails.append(r.email)
	
	print "people receiving the non-admin daily update"
	print to_emails

	if len(to_emails) == 0:
		return None
	
	c = Context({
		'today': today,
		'domain': Site.objects.get_current().domain,
		'location': location,
		'arriving' : arriving_today,
		'departing' : departing_today,
		'events_today': events_today,
	})
	text_content, html_content = render_templates(c, location, LocationEmailTemplate.GUEST_DAILY)

	mailgun_data={
		"from": location.from_email(),
		"to": to_emails,
		"subject": subject,
		"text": text_content,
	}
	if html_content:
		mailgun_data["html"] = html_content

	return mailgun_send(mailgun_data)

def admin_daily_update(location):
	# this is split out by location because each location has a timezone that affects the value of 'today'
	today = timezone.localtime(timezone.now())
	arriving_today = Reservation.objects.filter(location=location).filter(arrive=today).filter(status='confirmed')
	maybe_arriving_today = Reservation.objects.filter(location=location).filter(arrive=today).filter(status='approved')
	pending_now = Reservation.objects.filter(location=location).filter(status='pending')
	approved_now = Reservation.objects.filter(location=location).filter(status='approved')
	departing_today = Reservation.objects.filter(location=location).filter(depart=today).filter(status='confirmed')
	events_today = published_events_today_local(location=location)
	pending_or_feedback = events_pending(location=location)

	if not arriving_today and not departing_today and not events_today and not maybe_arriving_today and not pending_now and not approved_now:
		logger.debug("Nothing happening today at %s, skipping daily email" % location.name)
		return

	subject = "[%s] %s Events and Guests" % (location.email_subject_prefix, str(today.date()))
	
	admins_emails = []
	for admin in location.house_admins.all():
		if not admin.email in admins_emails:
			admins_emails.append(admin.email)
	if len(admins_emails) == 0:
		return None

	c = Context({
		'today': today,
		'domain': Site.objects.get_current().domain,
		'location': location,
		'arriving' : arriving_today,
		'maybe_arriving' : maybe_arriving_today,
		'pending_now' : pending_now,
		'approved_now' : approved_now,
		'departing' : departing_today,
		'events_today': events_today,
		'events_pending': pending_or_feedback['pending'],
		'events_feedback': pending_or_feedback['feedback'],
	})
	text_content, html_content = render_templates(c, location, LocationEmailTemplate.ADMIN_DAILY)

	mailgun_data={
		"from": location.from_email(),
		"to": admins_emails,
		"subject": subject,
		"text": text_content,
	}
	if html_content:
		mailgun_data["html"] = html_content

	return mailgun_send(mailgun_data)

############################################
#              EMAIL ENDPOINTS             #
############################################

@csrf_exempt
def current(request, location_slug):
	''' email all residents, guests and admins who are current or currently at this location. '''
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		logger.error('location not found')
		return HttpResponse(status=200)
	logger.debug('current@ for location: %s' % location)
	today = timezone.localtime(timezone.now())

	# we think that message_headers is a list of strings
	header_txt = request.POST.get('message-headers')
	message_headers = json.loads(header_txt)
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
	for r in Reservation.objects.confirmed_on_date(today, location):
		current_emails.append(r.user.email)

	# Add all the residents at this location
	for r in location.residents.all():
		current_emails.append(r.email)

	# Add the house admins
	for a in location.house_admins.all():
		current_emails.append(a.email)

	# Now loop through all the emails and build the bcc list we will use.
	# This makes sure there are no duplicate emails.
	bcc_list = []
	for email in current_emails:
		if email not in bcc_list:
			bcc_list.append(email)
	logger.debug("bcc list: %s" % bcc_list)
	
	# Make sure this person can post to our list
	#if not sender in bcc_list:
	#	# TODO - This shoud possibly send a response so they know they were blocked
	#	logger.warn("Sender (%s) not allowed.  Exiting quietly." % sender)
	#	return HttpResponse(status=200)
	if sender in bcc_list:
		bcc_list.remove(sender)
	
	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] [Current Guests and Residents] " 
		subject = prefix + subject
	logger.debug("subject: %s" % subject)

	# add in footer
	text_footer = '''\n\n-------------------------------------------\nYou are receving this email because you are a current guest or resident at %s. This list is used to share questions, ideas and activities with others currently at this location. Feel free to respond.'''% location.name
	body_plain = body_plain + text_footer
	if body_html:
		html_footer = '''<br><br>-------------------------------------------<br>You are receving this email because you are a current guest or resident at %s. This list is used to share questions, ideas and activities with others currently at this location. Feel free to respond.'''% location.name
		body_html = body_html + html_footer

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
def test80085(request, location_slug):
	''' test route '''
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		return HttpResponse(status=200)
	logger.debug('stay@ for location: %s' % location)
	logger.debug(request.POST)

	# we think that message_headers is a list of strings
	header_txt = request.POST.get('message-headers')
	message_headers = json.loads(header_txt)
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
	to = request.POST.get('To')
	from_address = request.POST.get('from')
	logger.debug('from: %s' % from_address)
	sender = request.POST.get('sender')
	logger.debug('sender: %s' % sender)	
	subject = request.POST.get('subject')
	body_plain = request.POST.get('body-plain')
	body_html = request.POST.get('body-html')

	# retrieve the current house admins for this location
	bcc_list = ['jsayles@gmail.com', 'jessy@jessykate.com']
	logger.debug("bcc list: %s" % bcc_list)

	# Make sure this person can post to our list
	#if not sender in bcc_list:
	#	# TODO - This shoud possibly send a response so they know they were blocked
	#	logger.warn("Sender (%s) not allowed.  Exiting quietly." % sender)
	#	return HttpResponse(status=200)
	
	# usually we would remove the sender from receiving the email but because
	# we're testing, let 'em have it.  
	#if sender in bcc_list:
	#	bcc_list.remove(sender)

	# pass through attachments
	# logger.debug(request)
	# logger.debug(request.FILES)
	# for attachment in request.FILES.values():
	# 	# JKS NOTE! this does NOT work with unicode-encoded data. i'm not
	# 	# actually sure that we should *expect* to receive unicode-encoded
	# 	# attachments, but it definitely breaks (which i disocvered because
	# 	# mailgun sends its test POST with a unicode-encoded attachment). 
	# 	a_file = default_storage.save(attachment.name, ContentFile(attachment.read()))
	# attachments = {}
	# num = 0
	# for attachment in request.FILES.values():
	# 	attachments["attachment-%d" % num] = (attachment.name, default_storage.open(attachment.name, 'rb').read())
	# 	#default_storage.delete(attachment.name)
	# 	num+= 1

	logger.debug(request)
	logger.debug(request.FILES)
	num = 0
	attachments = {}
	for attachment in request.FILES.values():
		attachments["attachment-%d" % num] = (attachment.name, attachment.read())
		num+= 1

	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find('EN Test') < 0:
		prefix = "[EN Test!] "
		subject = prefix + subject
	logger.debug("subject: %s" % subject)

	# add in footer
	text_footer = '''\n\n-------------------------------------------\nYou are receiving this email because someone at Embassy Network wanted to use you as a guinea pig.'''
	body_plain = body_plain + text_footer
	if body_html:
		html_footer = '''<br><br>-------------------------------------------<br>You are receiving this email because someone at Embassy Network wanted to use you as a guinea pig.''' 
		body_html = body_html + html_footer

	# send the message 
	list_address = "test80085@"+location.slug+".mail.embassynetwork.com"
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
			"h:Reply-To": from_address
		}
	return mailgun_send(mailgun_data, attachments)



@csrf_exempt
def stay(request, location_slug):
	''' email all admins at this location.'''
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		return HttpResponse(status=200)
	logger.debug('stay@ for location: %s' % location)
	logger.debug(request.POST)

	# we think that message_headers is a list of strings
	header_txt = request.POST.get('message-headers')
	message_headers = json.loads(header_txt)
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
	to = request.POST.get('To')
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

	# Make sure this person can post to our list
	#if not sender in bcc_list:
	#	# TODO - This shoud possibly send a response so they know they were blocked
	#	logger.warn("Sender (%s) not allowed.  Exiting quietly." % sender)
	#	return HttpResponse(status=200)
	if sender in bcc_list:
		bcc_list.remove(sender)

	# pass through attachments
	#logger.debug(request)
	#logger.debug(request.FILES)
	#for attachment in request.FILES.values():
	#	a_file = default_storage.save('/tmp/'+attachment.name, ContentFile(attachment.read()))
	attachments = {}
	#num = 0
	#for attachment in request.FILES.values():
	#	attachments["attachment[%d]"] = (attachment.name, open('/tmp/'+attachment.name, 'rb'))
	#	num+= 1

	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] [Admin] " 
		subject = prefix + subject
	logger.debug("subject: %s" % subject)

	# add in footer
	text_footer = '''\n\n-------------------------------------------\nYou are receving email to %s because you are a location admin at %s. Send mail to this list to reach other admins.''' % (recipient, location.name)
	body_plain = body_plain + text_footer
	if body_html:
		html_footer = '''<br><br>-------------------------------------------<br>You are receving email to %s because you are a location admin at %s. Send mail to this list to reach other admins.''' % (recipient, location.name)
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
			"h:Reply-To": from_address
		}
	return mailgun_send(mailgun_data, attachments)

# XXX TODO there is a lot of duplication in these email endpoints. should be
# able to pull out this code into some common reuseable functions. 
@csrf_exempt
def residents(request, location_slug):
	''' email all residents at this location.'''

	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		logger.error('location not found')
		return HttpResponse(status=200)
	logger.debug('residents@ for location: %s' % location)

	# we think that message_headers is a list of strings
	header_txt = request.POST.get('message-headers')
	message_headers = json.loads(header_txt)
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

	# Add all the residents at this location
	resident_emails = [] 
	for r in location.residents.all():
		resident_emails.append(r.email)

	# Now loop through all the emails and build the bcc list we will use.
	# This makes sure there are no duplicate emails.
	bcc_list = []
	for email in resident_emails:
		if email not in bcc_list:
			bcc_list.append(email)
	logger.debug("bcc list: %s" % bcc_list)
	
	# Make sure this person can post to our list
	#if not sender in bcc_list:
	#	# TODO - This shoud possibly send a response so they know they were blocked
	#	logger.warn("Sender (%s) not allowed.  Exiting quietly." % sender)
	#	return HttpResponse(status=200)
	if sender in bcc_list:
		bcc_list.remove(sender)
	
	# pass through attachments
	#logger.debug(request)
	#logger.debug(request.FILES)
	#to_attach = []
	#for attachment in request.FILES.values():
	#	a_file = default_storage.save(attachment.name, ContentFile(attachment.read()))
	#	to_attach.append(a_file)
	#num=0
	attachments = {}
	#for f in to_attach:
	#	attachments["attachment[%d]" % num] = (f.name, default_storage.open(f.name).read())
	#	default_storage.delete(attachment)
	#	num+= 1

	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] " 
		subject = prefix + subject
	logger.debug("subject: %s" % subject)

	# add in footer
	text_footer = '''\n\n-------------------------------------------\n*~*~*~* %s residents email list *~*~*~* '''% location.name
	body_plain = body_plain + text_footer

	if body_html:
		html_footer = '''<br><br>-------------------------------------------<br>*~*~*~* %s residents email list *~*~*~* '''% location.name
		body_html = body_html + html_footer

	# send the message 
	list_address = "residents@%s.%s" % (location.slug, settings.LIST_DOMAIN)
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
	return mailgun_send(mailgun_data, attachments)

