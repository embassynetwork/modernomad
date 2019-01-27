import contextlib
import io

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

from faker import Faker

from core.factory_apps import location
from core.factory_apps import communication
from core.factory_apps import events
from core.factory_apps import payment
from core.factory_apps import user
from core.factory_apps import accounts
from core.models import Currency


class Command(BaseCommand):
    help = 'Generate test data for a development environment.'

    def handle(self, *args, **options):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            call_command('sqlflush')
        flush_db = f.getvalue()

        with connection.cursor() as cursor:
            statements = flush_db.split('\n')
            for statement in statements:
                if not statement:
                    continue
                cursor.execute(statement)

        call_command('migrate')

        # setting the seed so output is consistent
        fake = Faker()
        fake.seed(1)

        # create a known super user. as the first created user, this user will
        # have user id = 1. this user will also be set as a location admin for
        # all locations.
        superuser = user.UserFactory(
            first_name='Root',
            last_name='Admin',
            username='admin',
            is_superuser=True,
            is_staff=True
        )

        # the site as a whole makes use of at least a fiat (USD) and DRFT
        # currency.
        accounts.USDCurrencyFactory.create()
        accounts.DRFTCurrencyFactory.create()

        # communication. these emails will also generate users.
        communication.EmailtemplateFactory()

        # Building location specific things
        for _ in range(10):
            locationobj = location.LocationFactory()
            resource = location.ResourceFactory(location=locationobj)
            location.LocationFee(location=locationobj)

            menu = location.LocationMenuFactory(location=locationobj)
            location.LocationFlatPageFactory(menu=menu)


            location.CapacityChangeFactory(resource=resource)
            # generates new users who will also be the location residents
            backing = location.BackingFactory(resource=resource)

            # event things
            event_admin = events.EventAdminGroupFactory(location=locationobj)
            event_series = events.EventSeriesFactory()
            events.EventFactory(
                location=locationobj, admin=event_admin, series=event_series
            )
            events.EventNotificationFactory()

            # payment
            subscription = payment.SubscriptionFactory(location=locationobj)
            payment.SubscriptionBillFactory(subscription=subscription)

            bill = payment.BookingBillFactory()
            payment.BillLineItem(bill=bill)
            use = payment.UseFactory(location=locationobj, resource=resource)
            payment.BookingFactory(bill=bill, use=use)

            payment.PaymentFactory(bill=bill)

        self.stdout.write(self.style.SUCCESS('Successfully generated testdata'))
