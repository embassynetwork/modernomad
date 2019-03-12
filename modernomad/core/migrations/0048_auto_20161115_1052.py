# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_auto_20161115_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='admins',
            field=models.ManyToManyField(help_text=b'May be blank', related_name='accounts_administered', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='owner',
            field=models.ForeignKey(related_name='accounts_owned', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'May be blank for group accounts', null=True),
        ),
    ]
