# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20160610_0820'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(help_text=b'Optional. Most locations operate primarily by email, but a phone number can be helpful for last minute coordination and the unexpected.', max_length=20, null=True, blank=True),
        ),
    ]
