# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import modernomad.core.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0020_auto_20160729_0556'),
    ]

    operations = [
        migrations.RenameModel(old_name='Room', new_name='Resource'),
        migrations.RenameField(
            model_name='reservable',
            old_name = 'room',
            new_name='resource'
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name = 'room',
            new_name='resource'
        ),
        migrations.RenameField(
            model_name='roomimage',
            old_name = 'room',
            new_name='resource'
        ),
    ]
