# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gather', '0006_auto_20150530_1937'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Location',
        ),
    ]
