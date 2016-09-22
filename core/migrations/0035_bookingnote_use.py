# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20160922_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingnote',
            name='use',
            field=models.ForeignKey(related_name='use_notes', blank=True, to='core.Use', null=True),
        ),
    ]
