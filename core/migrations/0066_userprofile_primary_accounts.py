# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0007_auto_20161221_1222'),
        ('core', '0065_remove_backing_accepts_drft'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='primary_accounts',
            field=models.ManyToManyField(help_text=b'one for each currency', related_name='primary_for', to='bank.Account'),
        ),
    ]
