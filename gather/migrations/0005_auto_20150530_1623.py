# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gather', '0004_auto_20150528_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventadmingroup',
            name='location',
            field=models.OneToOneField(related_name='event_admin_group', to='core.Location'),
        ),
    ]
