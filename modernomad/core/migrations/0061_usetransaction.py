# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0006_auto_20161120_1030'),
        ('core', '0060_use_accounted_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='UseTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction', models.ForeignKey(to='bank.Transaction')),
                ('use', models.ForeignKey(to='core.Use')),
            ],
        ),
    ]
