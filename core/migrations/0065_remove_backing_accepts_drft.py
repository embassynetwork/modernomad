# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0064_auto_20161211_0733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backing',
            name='accepts_drft',
        ),
    ]
