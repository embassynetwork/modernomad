import datetime
from django.core.management.base import BaseCommand
from ... import tasks
from gather import tasks as gather_tasks


class Command(BaseCommand):
    help = 'Run daily scheduled tasks from Heroku Scheduler, or similar.'

    def handle(self, *args, **kwargs):
        tasks.generate_subscription_bills()
        tasks.send_guests_residents_daily_update()
        tasks.send_admin_daily_update()
        tasks.send_guest_welcome()
        tasks.send_departure_email()
        tasks.slack_embassysf_daily()
        gather_tasks.events_today_reminder()
        if datetime.date.today().weekday() == 6: # sunday
            gather_tasks.weekly_upcoming_events()

