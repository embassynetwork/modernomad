# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0005_auto_20161120_0922'),
        ('core', '0056_houseaccount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backing',
            name='account',
        ),
        migrations.AddField(
            model_name='backing',
            name='drft_account',
            field=models.ForeignKey(related_name='+', default=1, to='bank.Account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='backing',
            name='money_account',
            field=models.ForeignKey(related_name='+', default=2, to='bank.Account'),
            preserve_default=False,
        ),
    ]
