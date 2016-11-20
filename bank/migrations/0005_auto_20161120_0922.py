# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_auto_20161120_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='transaction',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 20, 17, 22, 58, 790015, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
