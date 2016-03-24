from celery.task.schedules import crontab
from celery.task import periodic_task
from core.models import Reservation, Location, Subscription
from core.emails import guests_residents_daily_update, admin_daily_update, guest_welcome, goodbye_email
from modernomad.backup import BackupManager
import datetime
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)

#@periodic_task(run_every=crontab(hour=22, minute=53, day_of_week="*"))  
#def test():      
#    print "HELLO WORLD"                    

@periodic_task(run_every=crontab(hour=5, minute=30))
def send_guests_residents_daily_update():
	locations = Location.objects.all()
	for location in locations:
		guests_residents_daily_update(location)

@periodic_task(run_every=crontab(hour=4, minute=30))
def send_admin_daily_update():
	locations = Location.objects.all()
	for location in locations:
		admin_daily_update(location)

#@periodic_task(run_every=crontab(minute="*")) # <-- for testing
@periodic_task(run_every=crontab(hour=5, minute=0))
def send_guest_welcome():
	# get all reservations WELCOME_EMAIL_DAYS_AHEAD from now. 
	locations = Location.objects.all()
	for location in locations:
		soon = datetime.datetime.today() + datetime.timedelta(days=location.welcome_email_days_ahead)
		upcoming = Reservation.objects.filter(location=location).filter(arrive=soon).filter(status='confirmed')
		for reservation in upcoming:
			guest_welcome(reservation)

@periodic_task(run_every=crontab(hour=4, minute=30))
def send_departure_email():
	# get all reservations departing today
	locations = Location.objects.all()
	for location in locations:
		today = timezone.localtime(timezone.now())
		departing = Reservation.objects.filter(location=location).filter(depart=today).filter(status='confirmed')
		for reservation in departing:
			print 'sending goodbye email to %s' % reservation.user.email
			goodbye_email(reservation)

@periodic_task(run_every=crontab(hour=2, minute=0))
def make_backup():
	manager = BackupManager()
	manager.make_backup()


@periodic_task(run_every=crontab(hour=1, minute=0))
def generate_subscription_bills():
	today = timezone.localtime(timezone.now()).date()
	# using the exclude is an easier way to filter for subscriptions with an
	# end date of None *or* in the future.
	locations = Location.objects.all()
	for l in locations:
		subscriptions_ready = Subscription.objects.ready_for_billing(location=l, target_date=today)
		if len(subscriptions_ready) == 0:
			logger.debug('no subscriptions are ready for billing at %s today.' % l.name)
		for s in subscriptions_ready:
			logger.debug('')
			logger.debug('automatically generating bill for subscription %d' % s.id)
			# JKS - we *could* double check to see whether there is already a
			# bill for this date. but, i'm worried about edge cases, and the
			# re-generation is non-destructive, so I just call generate_bill
			# regardless. if we end up with a lot of subscriptions we'll need
			# to revisit this)
			s.generate_bill(target_date=today)



