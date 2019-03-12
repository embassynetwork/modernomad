# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_auto_20161209_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='residents',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='residents',
        ),
        migrations.AddField(
            model_name='backing',
            name='end',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='backing',
            name='start',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
