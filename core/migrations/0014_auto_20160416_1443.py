# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20160312_1619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='public',
        ),
        migrations.AddField(
            model_name='location',
            name='visibility',
            field=models.CharField(default=b'link', max_length=32, choices=[(b'public', b'Public'), (b'members', b'Members Only'), (b'link', b'Those with the Link')]),
        ),
        migrations.AlterField(
            model_name='locationemailtemplate',
            name='key',
            field=models.CharField(max_length=32, choices=[(b'admin_daily_update', b'Admin Daily Update'), (b'guest_daily_update', b'Guest Daily Update'), (b'invoice', b'Invoice'), (b'receipt', b'Reservation Receipt'), (b'subscription_receipt', b'Subscription Receipt'), (b'newreservation', b'New Reservation'), (b'pre_arrival_welcome', b'Pre-Arrival Welcome'), (b'departure', b'Departure')]),
        ),
    ]
