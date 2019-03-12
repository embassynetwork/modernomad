# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20161116_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.ForeignKey(related_name='accounts', default=1, to='bank.Currency'),
            preserve_default=False,
        ),
    ]
