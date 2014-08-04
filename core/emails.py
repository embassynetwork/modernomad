from django.contrib.auth.models import User
from django.core import urlresolvers
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import Site
from models import get_location
from django.http import HttpResponse, HttpResponseRedirect
from gather.tasks import published_events_today_local, events_pending
from django.utils import timezone
import requests
import datetime

weekday_number_to_name = {
	0: "Monday",
	1: "Tuesday",
	2: "Wednesday",
	3: "Thursday",
	4: "Friday",
	5: "Saturday",
	6: "Sunday"
}

def current(request, location_slug):
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		return HttpResponse(status=200)

	# make sure this isn't an email we have already forwarded (cf. emailbombgate 2014)
	# A List-Id header will only be present if it has been added manually in
	# this function, ie, if we have already processed this message. 
	if request.POST.get('List-Id'):
		# mailgun requires a code 200 or it will continue to retry delivery
		return HttpResponse(status=200)
	if message['Auto-Submitted'] and message['Auto-Submitted'] != 'no':
		return HttpResponse(status=200)

	# TODO? make sure the sender is on the list?

	print request.POST
	recipient = request.POST.get('recipient')
	from_address = request.POST.get('from')
	sender = request.POST.get('sender')
	print 'sender is: %s' % sender

	subject = request.POST.get('subject')
	body_plain = request.POST.get('body-plain')
	body_html = request.POST.get('body-html')

	# find who is currently at this location and add them to a bcc list 
	reservations_here_today = Reservation.today.confirmed(location)
	guest_emails = []
	for r in reservations_here_today:
		guest_emails.append(r.user.email)

	residents = location.residents.all()
	resident_emails = []
	for person in residents:
		resident_emails.append(person.email)
	current_emails = guest_emails + resident_emails 

	bcc_list = []
	for person in current_emails:
		if person.email not in bcc_list:
			bcc_list.append(person.email)
	print bcc_list

	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] [Current Guests and Residents] " 
		subject = prefix + subject
	print subject

	# add in footer
	footer = '''\n\n-------------------------------------------\nYou are receving this email because you are a current guest or resident at %s. This list is used to share questions, ideas and activities with others currently at this location. Feel free to respond.'''% location.name
	body_plain = body_plain + footer
	body_html = body_html + footer

	# send the message 
	mailgun_api_key = settings.MAILGUN_API_KEY
	list_domain = settings.LIST_DOMAIN
	list_address = "current@%s.mail.embassynetwork.com" % location.slug
	resp = requests.post(
	    "https://api.mailgun.net/v2/%s/messages" % list_domain,
	    auth=("api", mailgun_api_key),
	    data={"from": from_address,
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
			"o:testmode": "yes"

		}
	)
	print resp.text
	return HttpResponse(status=200)

def stay(request, location_slug):
	# fail gracefully if location does not exist
	try:
		location = get_location(location_slug)
	except:
		# XXX TODO reject and bounce back to sender?
		return HttpResponse(status=200)

	# make sure this isn't an email we have already forwarded (cf. emailbombgate 2014)
	# A List-Id header will only be present if it has been added manually in
	# this function, ie, if we have already processed this message. 
	if request.POST.get('List-Id'):
		# mailgun requires a code 200 or it will continue to retry delivery
		return HttpResponse(status=200)
	if message['Auto-Submitted'] and message['Auto-Submitted'] != 'no':
		return HttpResponse(status=200)

	# TODO? make sure the sender is on the list?

	print request.POST
	recipient = request.POST.get('recipient')
	from_address = request.POST.get('from')
	sender = request.POST.get('sender')
	print 'sender is: %s' % sender
	
	subject = request.POST.get('subject')
	body_plain = request.POST.get('body-plain')
	body_html = request.POST.get('body-html')

	# retrieve the current house admins for this location
	location_admins = location.house_admins.all()
	bcc_list = []
	for person in location_admins:
		if person.email not in bcc_list:
			bcc_list.append(person.email)
	print bcc_list

	# prefix subject, but only if the prefix string isn't already in the
	# subject line (such as a reply)
	if subject.find(location.email_subject_prefix) < 0:
		prefix = "["+location.email_subject_prefix + "] [Admin] " 
		subject = prefix + subject
	print subject

	# add in footer
	footer = '''\n\n-------------------------------------------\nYou are receving email to %s because you are a location admin at %s. Send mail to this list to reach other admins.''' % (recipient, location.name)
	body_plain = body_plain + footer
	body_html = body_html + footer

	# send the message 
	mailgun_api_key = settings.MAILGUN_API_KEY
	list_domain = settings.LIST_DOMAIN
	list_address = location.from_email()
	resp = requests.post(
	    "https://api.mailgun.net/v2/%s/messages" % list_domain,
	    auth=("api", mailgun_api_key),
	    data={"from": from_address,
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
			"o:testmode": "yes"
		}
	)
	print resp.text
	return HttpResponse(status=200)

def send_from_location_address(subject, text_content, html_content, recipient, location):
	''' a somewhat generic send function using mailgun that sends plaintext
	from the location's generic stay@ address.'''

	mailgun_api_key = settings.MAILGUN_API_KEY
	list_domain = settings.LIST_DOMAIN
	location_address = location.from_email()
	if not html_content:
		html_content = text_content
	resp = requests.post(
		"https://api.mailgun.net/v2/%s/messages" % list_domain,
		auth=("api", mailgun_api_key),
		data={"from": location_address,
			"to": [recipient, ],
			"subject": subject,
			"text": text_content,
			"html": html_content,
			}
		)
	print resp.text
	return HttpResponse(status=200)

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

	resp = requests.post(
			"https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
			auth=("api", settings.MAILGUN_API_KEY),
			data={"from": sender,
				"to": [recipient, ],
				"subject": subject,
				"text": text_content,
				"html": html_content,
				}
			)
	print resp.text
	return True

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
	send_from_location_address(subject, text_content, html_context, recipient, self.location)
	self.save()

def new_reservation_notify(reservation):
	location = reservation.location
	house_admins = reservation.location.house_admins.all()

	domain = Site.objects.get_current().domain

	plaintext = get_template('emails/newreservation.txt')
	htmltext = get_template('emails/newreservation.html')

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
		"admin_url" : "http://" + domain + urlresolvers.reverse('reservation_manage', args=(reservation.location.slug, reservation.id,))
	})

	subject = "[%s] Reservation Request, %s %s, %s - %s" % (location.email_subject_prefix, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	sender = location.from_email()
	recipients = []
	for admin in house_admins:
		recipients.append(admin.email)
	text_content = plaintext.render(c)
	html_content = htmltext.render(c)

	resp = requests.post(
	    "https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
	    auth=("api", settings.MAILGUN_API_KEY),
	    data={"from": sender,
			"to": recipients,
			"subject": subject,
			"text": text_content,
			"html": html_content,
		}
	)
	print resp.text
	return HttpResponse(status=200)


def updated_reservation_notify(reservation):
	location = reservation.location
	house_admins = location.house_admins.all()
	subject = "[%s] Reservation Updated, %s %s, %s - %s" % (location.email_subject_prefix, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	sender = location.from_email()
	domain = Site.objects.get_current().domain
	admin_path = urlresolvers.reverse('reservation_manage', args=(reservation.location.slug, reservation.id,))
	text = '''Howdy, 

A reservation has been updated and requires your review. 

You can view, approve or deny this request at %s%s.''' % (domain, admin_path)
	# XXX TODO this is terrible. should have an alias and let a mail agent handle this!
	for admin in house_admins:
		recipient = [admin.email,]
		resp = requests.post(
			"https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
			auth=("api", settings.MAILGUN_API_KEY),
			data={"from": sender,
				"to": recipients,
				"subject": subject,
				"text": text_content,
				"html": html_content,
			}
		)
		print resp.text
		return HttpResponse(status=200)

def guest_daily_update(location):
	# this is split out by location because each location has a timezone that affects the value of 'today'
	today = datetime.date.today()
	
	# who should we tell?
	reservations_here_today = Reservation.today.confirmed(location)
	guest_emails = []
	for r in reservations_here_today:
		guest_emails.append(r.user.email)
	
	# who should we tell them about?
	arriving_today = Reservation.objects.filter(location=location).filter(arrive=today).filter(status='confirmed')
	departing_today = Reservation.objects.filter(location=location).filter(depart=today).filter(status='confirmed')
	domain = Site.objects.get_current().domain
	events_today = published_events_today_local(location=location)

	plaintext = get_template('emails/guest_daily_update.txt')
	c = Context({
		'arriving' : arriving_today,
		'departing' : departing_today,
		'domain': domain,
		'events_today': events_today,
		'location_name': location.name,
	})
	text_content = plaintext.render(c)
	subject = "[%s] Events, Arrivals and Departures for %s" % (location.email_subject_prefix, str(today))
	sender = location.from_email()
	for guest_email in guest_emails:
		resp = requests.post("https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
			auth=("api", settings.MAILGUN_API_KEY),
			data={
				"from": sender,
				"to": guest_email,
				"subject": subject,
				"text": text_content,
			}
		)
		print resp.text
		return HttpResponse(status=200)


def admin_daily_update(location):
	# this is split out by location because each location has a timezone that affects the value of 'today'

	today = datetime.datetime.today() 
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
	subject = "[%s] %s Events and Guests" % (location.email_subject_prefix, str(today))
	sender = location.from_email()
	house_admins = location.house_admins.all()
	for admin in house_admins:
		admin_email = admin.email
		resp = requests.post("https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
			auth=("api", settings.MAILGUN_API_KEY),
			data={
				"from": sender,
				"to": admin_email,
				"subject": subject,
				"text": text_content,
			}
		)
		print resp.text
		return HttpResponse(status=200)


def guest_welcome(reservation):
	''' Send guest a welcome email'''
	# this is split out by location because each location has a timezone that affects the value of 'today'
	domain = Site.objects.get_current().domain
	plaintext = get_template('emails/pre_arrival_welcome.txt')
	day_of_week = weekday_number_to_name[reservation.arrive.weekday()]
	c = Context({
		'first_name': reservation.user.first_name,
		'day_of_week' : day_of_week,
		'site_url': urlresolvers.reverse('location_home'),
		'house_code': location.house_access_code,
		'location_name': location.name,
		'address': location.address,
		'ssid': location.ssid,
		'ssid_password': location.ssid_password,
		'events_url' : domain + '/events/upcoming/',
		'current_email' : 'current@%s.mail.embassynetwork.com' % location.slug,
		'profile_url' : "https://" + domain + urlresolvers.reverse('user_detail', args=(reservation.user.username,)),
		'reservation_url' : "https://" + domain + urlresolvers.reverse('reservation_detail', args=(reservation.location.slug, reservation.id,)),
	})
	text_content = plaintext.render(c)
	subject = "[%s] See you on %s" % (location.email_subject_prefix, day_of_week)
	sender = location.from_email()
	recipient = [reservation.user.email,]
	resp = requests.post("https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
		auth=("api", settings.MAILGUN_API_KEY),
		data={
			"from": sender,
			"to": recipient,
			"subject": subject,
			"text": text_content,
		}
	)
	print resp.text
	return HttpResponse(status=200)

	

