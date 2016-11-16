# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_account_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit', models.OneToOneField(related_name='systemaccount_credit', to='core.Account')),
                ('currency', models.OneToOneField(to='core.Currency')),
                ('debits', models.OneToOneField(related_name='systemaccount_debit', to='core.Account')),
            ],
        ),
    ]
