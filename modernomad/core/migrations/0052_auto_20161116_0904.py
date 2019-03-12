# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_systemaccount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='systemaccount',
            old_name='credit',
            new_name='credits',
        ),
    ]
