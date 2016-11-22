# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_auto_20161120_0952'),
    ]

    operations = [
        migrations.RenameField(
            model_name='backing',
            old_name='accept_drft',
            new_name='accepts_drft',
        ),
    ]
