# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gather', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(related_name='events_attending', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='endorsements',
            field=models.ManyToManyField(related_name='events_endorsed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizers',
            field=models.ManyToManyField(related_name='events_organized', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='eventadmingroup',
            name='location',
            field=models.OneToOneField(to='core.Location'),
        ),
        migrations.AlterField(
            model_name='eventnotifications',
            name='location_weekly',
            field=models.ManyToManyField(related_name='event_notifications', to='core.Location'),
        ),
    ]
