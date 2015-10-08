# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150712_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='last4',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
