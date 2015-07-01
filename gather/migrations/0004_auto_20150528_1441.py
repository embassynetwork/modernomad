# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150505_0846'),
        ('gather', '0003_auto_20150505_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventnotifications',
            name='location_publish',
            field=models.ManyToManyField(related_name='event_published', to='core.Location'),
        ),
        migrations.AlterField(
            model_name='eventnotifications',
            name='location_weekly',
            field=models.ManyToManyField(related_name='weekly_event_notifications', to='core.Location'),
        ),
    ]
