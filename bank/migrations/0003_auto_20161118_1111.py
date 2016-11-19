# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0002_auto_20161117_0325'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transaction',
            name='valid',
            field=models.BooleanField(default=False),
        ),
    ]
