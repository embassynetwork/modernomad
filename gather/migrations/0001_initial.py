# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import gather.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('start', models.DateTimeField(verbose_name=b'Start time')),
                ('end', models.DateTimeField(verbose_name=b'End time')),
                ('title', models.CharField(max_length=300)),
                ('slug', models.CharField(help_text=b'This will be auto-suggested based on the event title, but feel free to customize it.', unique=True, max_length=60)),
                ('description', models.TextField(help_text=b'Basic HTML markup is supported for your event description.')),
                ('image', models.ImageField(upload_to=gather.models.event_img_upload_to)),
                ('notifications', models.BooleanField(default=True)),
                ('where', models.CharField(help_text=b'Either a specific room at this location or an address if elsewhere', max_length=500, verbose_name=b'Where will the event be held?')),
                ('organizer_notes', models.TextField(help_text=b'These will only be visible to other organizers', null=True, blank=True)),
                ('limit', models.IntegerField(default=0, help_text=b'Specify a cap on the number of RSVPs, or 0 for no limit.', blank=True)),
                ('private', models.BooleanField(default=False, help_text=b'Private events will only be seen by organizers, attendees, and those who have the link. It will not be displayed in the public listing.')),
                ('status', models.CharField(default=b'waiting for approval', max_length=200, verbose_name=b'Review Status', blank=True, choices=[(b'waiting for approval', b'Waiting for Approval'), (b'seeking feedback', b'Seeking Feedback'), (b'ready to publish', b'Ready to publish'), (b'live', b'Live'), (b'canceled', b'Canceled')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventAdminGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventNotifications',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reminders', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventSeries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.CharField(unique=True, max_length=60)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventnotifications',
            name='location_weekly',
            field=models.ManyToManyField(to='core.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventnotifications',
            name='user',
            field=models.OneToOneField(related_name='event_notifications', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventadmingroup',
            name='location',
            field=models.ForeignKey(to='core.Location', unique=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventadmingroup',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='admin',
            field=models.ForeignKey(related_name='events', to='gather.EventAdminGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(related_name='events_attending', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='creator',
            field=models.ForeignKey(related_name='events_created', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='endorsements',
            field=models.ManyToManyField(related_name='events_endorsed', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(to='core.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='organizers',
            field=models.ManyToManyField(related_name='events_organized', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='series',
            field=models.ForeignKey(related_name='events', blank=True, to='gather.EventSeries', null=True),
            preserve_default=True,
        ),
    ]
