# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0008_payment_last4'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaypiDoor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('api_key', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=128)),
                ('sync_ts', models.DateTimeField(null=True, blank=True)),
                ('location', models.ForeignKey(to='core.Location')),
            ],
        ),
        migrations.CreateModel(
            name='MaypiDoorCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('code', models.CharField(unique=True, max_length=16, db_index=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(null=True, blank=True)),
                ('sync_ts', models.DateTimeField(null=True, blank=True)),
                ('door', models.ForeignKey(to='core.MaypiDoor')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
