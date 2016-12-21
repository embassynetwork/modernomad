# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0006_auto_20161120_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='admins',
            field=models.ManyToManyField(help_text=b'May be blank', related_name='accounts_administered', verbose_name=b'Admins (optional)', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
