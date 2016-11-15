# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0044_auto_20161115_0926'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='users',
        ),
        migrations.AddField(
            model_name='account',
            name='admins',
            field=models.ManyToManyField(related_name='accounts_administered', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='account',
            name='owner',
            field=models.ForeignKey(related_name='accounts_owned', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
