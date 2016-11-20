# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_auto_20161120_0900'),
        ('core', '0054_auto_20161116_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accept_drft', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='bank.Account')),
                ('resource', models.ForeignKey(to='core.Resource')),
                ('subscription', models.ForeignKey(blank=True, to='core.Subscription', null=True)),
            ],
        ),
    ]
