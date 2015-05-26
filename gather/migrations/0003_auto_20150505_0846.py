# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gather', '0002_auto_20150421_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(related_name='events_attending', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='endorsements',
            field=models.ManyToManyField(related_name='events_endorsed', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizers',
            field=models.ManyToManyField(related_name='events_organized', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
