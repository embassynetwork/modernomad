# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_auto_20161120_0900'),
        ('core', '0055_backing'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account', models.ForeignKey(to='bank.Account')),
                ('location', models.ForeignKey(to='core.Location')),
            ],
        ),
    ]
