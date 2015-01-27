from celery.task.schedules import crontab
from celery.task import periodic_task
from core.models import Reservation, Location
from core.emails import guests_residents_daily_update, admin_daily_update, guest_welcome
from modernomad.backup import BackupManager
import datetime

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
@periodic_task(run_every=crontab(hour=2, minute=0))
def send_guest_welcome():
	# get all reservations WELCOME_EMAIL_DAYS_AHEAD from now. 
	locations = Location.objects.all()
	for location in locations:
		soon = datetime.datetime.today() + datetime.timedelta(days=location.welcome_email_days_ahead)
		upcoming = Reservation.objects.filter(location=location).filter(arrive=soon).filter(status='confirmed')
		for reservation in upcoming:
			guest_welcome(reservation)

@periodic_task(run_every=crontab(hour=2, minute=0))
def send_departure_email():
	# get all reservations departing today
	locations = Location.objects.all()
	for location in locations:
		today = timezone.localtime(timezone.now())
		departing = Reservation.objects.filter(location=location).filter(arrivedepart=today).filter(status='confirmed')
		for reservation in departing:
			goodbye_email(reservation)

@periodic_task(run_every=crontab(hour=1, minute=0))
def make_backup():
	manager = BackupManager()
	manager.make_backup()



