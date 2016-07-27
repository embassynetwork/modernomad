# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20160727_0305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='num_beds',
        ),
        migrations.RemoveField(
            model_name='room',
            name='residents',
        ),
        migrations.RemoveField(
            model_name='room',
            name='shared',
        ),
    ]
