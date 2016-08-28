# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160808_0252'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='availability',
            options={'verbose_name_plural': 'Availabilities'},
        ),
        migrations.RenameField(
            model_name='availability',
            old_name='number',
            new_name='quantity',
        ),
    ]
