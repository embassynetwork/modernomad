from celery.task.schedules import crontab
from celery.task import periodic_task
from core.models import Reservation, UserProfile
from django.contrib.auth.models import User
import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import get_template
from django.template import Context
from django.core import urlresolvers
from django.core.mail import EmailMultiAlternatives

weekday_number_to_name = {
	0: "Monday",
	1: "Tuesday",
	2: "Wednesday",
	3: "Thursday",
	4: "Friday",
	5: "Saturday",
	6: "Sunday"
}


#@periodic_task(run_every=crontab(hour=22, minute=53, day_of_week="*"))  
#def test():      
#    print "HELLO WORLD"                    

@periodic_task(run_every=crontab(hour=4, minute=30))
#@periodic_task(run_every=crontab(minute="*")) # <-- for testing
def admin_today_notification():
	today = datetime.datetime.today() 
	arriving_today = Reservation.objects.filter(arrive=today).filter(status='confirmed')
	departing_today = Reservation.objects.filter(depart=today).filter(status='confirmed')
	domain = Site.objects.get_current().domain
	plaintext = get_template('emails/admin_today_notification.txt')
	c = Context({
		'arriving' : arriving_today,
		'departing' : departing_today,
		'domain': domain,
	})
	text_content = plaintext.render(c)
	subject = "[Embassy SF] Guest Arrivals and Departures for %s" % (str(today))
	sender = settings.DEFAULT_FROM_EMAIL
	# XXX this is a temporary hack until we make this a setting on the
	# house admin accounts. 
	house_admins = User.objects.filter(groups__name='house_admin')
	recipients = []
	for admin in house_admins:
		recipients.append(admin.email)
	msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
	msg.send()

@periodic_task(run_every=crontab(hour=2, minute=0))
#@periodic_task(run_every=crontab(minute="*")) # <-- for testing
def guest_welcome():
	# get all reservations WELCOME_EMAIL_DAYS_AHEAD from now. 
	soon = datetime.datetime.today() + datetime.timedelta(days=settings.WELCOME_EMAIL_DAYS_AHEAD)
	upcoming = Reservation.objects.filter(arrive=soon).filter(status='confirmed')
	send_guest_welcome(upcoming)

def send_guest_welcome(upcoming):
	''' does the work of sending a guest welcome email, whether by scheduled
	task or manually for imminent reservations.'''
	# 'upcoming' needs to be a queryset
	domain = Site.objects.get_current().domain
	plaintext = get_template('emails/pre_arrival_welcome.txt')
	for reservation in upcoming:
		day_of_week = weekday_number_to_name[reservation.arrive.weekday()]
		c = Context({
			'first_name': reservation.user.first_name,
			'day_of_week' : day_of_week,
			'site_url': domain,
			'events_url' : settings.EVENTS_LINK,
			'facebook_group' : settings.FACEBOOK_GROUP,
			'profile_url' : "https://" + domain + urlresolvers.reverse('user_details', args=(reservation.user.id,)),
			'reservation_url' : "https://" + domain + urlresolvers.reverse('reservation_detail', args=(reservation.id,)),
		})
		text_content = plaintext.render(c)
		subject = "[Embassy SF] See you on %s" % day_of_week
		sender = settings.DEFAULT_FROM_EMAIL
		recipients = [reservation.user.email,]
		msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
		msg.send()


