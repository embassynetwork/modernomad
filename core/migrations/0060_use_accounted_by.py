# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_auto_20161120_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='use',
            name='accounted_by',
            field=models.CharField(default=b'fiat', max_length=200, blank=True, choices=[(b'fiat', b'Fiat'), (b'fiatdrft', b'Fiat & DRFT'), (b'drft', b'DRFT'), (b'backing', b'Backing')]),
        ),
    ]
