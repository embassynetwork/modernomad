# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0037_auto_20160922_0407'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BookingNote',
            new_name='UseNote',
        ),
    ]
