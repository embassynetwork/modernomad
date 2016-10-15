# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20161001_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='capacitychange',
            name='resource',
            field=models.ForeignKey(related_name='capacity_changes', to='core.Resource'),
        ),
    ]
