# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20160922_0403'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookingnote',
            old_name='booking',
            new_name='booking_deprecated',
        ),
    ]
