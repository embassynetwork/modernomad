# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160720_0553'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookableresource',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 27, 10, 5, 50, 881585, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookableresource',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 27, 10, 5, 55, 713448, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
