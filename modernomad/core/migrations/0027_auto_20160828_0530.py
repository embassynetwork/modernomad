# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20160828_0523'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservable',
            name='resource',
        ),
        migrations.DeleteModel(
            name='Reservable',
        ),
    ]
