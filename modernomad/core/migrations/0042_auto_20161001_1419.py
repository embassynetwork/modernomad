# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_merge'),
    ]

    operations = [
        migrations.RenameModel(old_name='Availability', new_name='CapacityChange')
    ]
