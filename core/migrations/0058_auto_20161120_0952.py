# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20161120_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backing',
            name='resource',
            field=models.OneToOneField(to='core.Resource'),
        ),
    ]
