from django.core.management.base import BaseCommand
from ... import tasks
from gather import tasks as gather_tasks

TASKS = {
    'residents_daily_update': tasks.send_guests_residents_daily_update,
    'admin_daily_update': tasks.send_admin_daily_update,
    'guest_welcome': tasks.send_guest_welcome,
    'departure_email': tasks.send_departure_email,
    'make_backup': tasks.make_backup,
    'generate_subscription_bills': tasks.generate_subscription_bills,
    'slack_embassy_daily': tasks.slack_embassysf_daily,
    'slack_ams_daily': tasks.slack_ams_daily,
    'slack_redvic_daily': tasks.slack_redvic_daily,

    'events_today_reminder': gather_tasks.events_today_reminder,
    'weekly_upcoming_events': gather_tasks.weekly_upcoming_events,
}


class Command(BaseCommand):
    help = 'Execute tasks with heroku scheduler.'

    def add_arguments(self, parser):
        parser.add_argument('function', type=str, help='The function to run')

    def handle(self, *args, **kwargs):
        func_name = kwargs['function']
        func = TASKS[func_name]
        func()
