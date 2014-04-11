from django.contrib.auth.models import User
from django.core import urlresolvers
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import Site
from django.conf import settings
import datetime

def send_receipt(reconcile):
	# make sure we have all the data we need. 
	if (not reconcile.paid_amount or not reconcile.payment_method or not reconcile.transaction_id 
			or not reconcile.payment_date or not reconcile.PAID):
		raise Exception("reservation must be unpaid or paid to generate receipt")
		return False

	total_paid = reconcile.paid_amount

	plaintext = get_template('emails/receipt.txt')
	htmltext = get_template('emails/receipt.html')
	c = Context({
		'first_name': reconcile.reservation.user.first_name, 
		'last_name': reconcile.reservation.user.last_name, 
		'res_id': reconcile.reservation.id,
		'today': datetime.datetime.today(), 
		'arrive': reconcile.reservation.arrive, 
		'depart': reconcile.reservation.depart, 
		'room': reconcile.reservation.room.name, 
		'num_nights': reconcile.reservation.total_nights(), 
		'rate': reconcile.get_rate(), 
		'payment_method': reconcile.payment_method,
		'transaction_id': reconcile.transaction_id,
		'payment_date': reconcile.payment_date,
		'total_paid': total_paid,
	}) 

	subject = "%s Receipt for your Stay %s - %s" % (settings.EMAIL_SUBJECT_PREFIX, str(reconcile.reservation.arrive), str(reconcile.reservation.depart))  
	sender = settings.DEFAULT_FROM_EMAIL
	recipients = [reconcile.reservation.user.email,]
	text_content = plaintext.render(c)
	html_content = htmltext.render(c)
	msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
	msg.attach_alternative(html_content, "text/html")
	msg.send()
	return True

# send house_admins notification of new reservation. use the post_save signal
# so that a) we can be sure the reservation was successfully saved, and b) the
# unique ID of this reservation only exists post-save.
def new_reservation_notify(reservation):
	house_admins = reservation.location.house_admins.all()

	domain = Site.objects.get_current().domain
	subject = "%s Reservation Request, %s %s, %s - %s" % (settings.EMAIL_SUBJECT_PREFIX, reservation.user.first_name, 
	reservation.user.last_name, str(reservation.arrive), str(reservation.depart))

	plaintext = get_template('emails/newreservation.txt')
	htmltext = get_template('emails/newreservation.html')

	c = Context({
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

	subject = "%s Reservation Request, %s %s, %s - %s" % (settings.EMAIL_SUBJECT_PREFIX, reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	sender = settings.DEFAULT_FROM_EMAIL
	recipients = []
	for admin in house_admins:
		recipients.append(admin.email)
	text_content = plaintext.render(c)
	html_content = htmltext.render(c)
	msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
	msg.attach_alternative(html_content, "text/html")
	msg.send()

def updated_reservation_notify(reservation):
	house_admins = reservation.location.house_admins.all()
	subject = "[Embassy SF] Reservation Updated, %s %s, %s - %s" % (reservation.user.first_name, 
		reservation.user.last_name, str(reservation.arrive), str(reservation.depart))
	sender = settings.DEFAULT_FROM_EMAIL
	domain = Site.objects.get_current().domain
	admin_path = urlresolvers.reverse('reservation_manage', args=(reservation.location.slug, reservation.id,))
	text = '''Howdy, 

A reservation has been updated and requires your review. 

You can view, approve or deny this request at %s%s.''' % (domain, admin_path)
	# XXX TODO this is terrible. should have an alias and let a mail agent handle this!
	for admin in house_admins:
		recipient = [admin.email,]
		send_mail(subject, text, sender, recipient) 

