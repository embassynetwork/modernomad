# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0063_auto_20161209_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='capacitychange',
            options={},
        ),
        migrations.AddField(
            model_name='capacitychange',
            name='accept_drft',
            field=models.BooleanField(default=False),
        ),
    ]
