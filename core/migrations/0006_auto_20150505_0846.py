# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150421_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='residents',
            field=models.ManyToManyField(related_name='residences', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='locationemailtemplate',
            name='key',
            field=models.CharField(max_length=32, choices=[(b'admin_daily_update', b'Admin Daily Update'), (b'guest_daily_update', b'Guest Daily Update'), (b'invoice', b'Invoice'), (b'receipt', b'Receipt'), (b'newreservation', b'New Reservation'), (b'pre_arrival_welcome', b'Pre-Arrival Welcome'), (b'departure', b'Departure')]),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='suppressed_fees',
            field=models.ManyToManyField(to='core.Fee', blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='residents',
            field=models.ManyToManyField(help_text=b'This field is optional.', related_name='residents', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
