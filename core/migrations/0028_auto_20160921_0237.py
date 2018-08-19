# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0027_auto_20160828_0530'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Reservation',
            new_name='Booking',
        ),
        migrations.RenameModel(
            old_name='ReservationNote',
            new_name='BookingNote',
        ),
        migrations.RenameModel(
            old_name='ReservationBill',
            new_name='BookingBill',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='max_reservation_days',
            new_name='max_booking_days',
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='context',
            field=models.CharField(max_length=32, choices=[(b'booking', b'Booking'), (b'subscription', b'Subscription')]),
        ),
        migrations.AlterField(
            model_name='locationemailtemplate',
            name='key',
            field=models.CharField(max_length=32, choices=[(b'admin_daily_update', b'Admin Daily Update'), (b'guest_daily_update', b'Guest Daily Update'), (b'invoice', b'Invoice'), (b'receipt', b'Booking Receipt'), (b'subscription_receipt', b'Subscription Receipt'), (b'newbooking', b'New Booking'), (b'pre_arrival_welcome', b'Pre-Arrival Welcome'), (b'departure', b'Departure')]),
        ),
    ]
