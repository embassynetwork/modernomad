# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20161116_0959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='admins',
        ),
        migrations.RemoveField(
            model_name='account',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='account',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='account',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='transaction',
        ),
        migrations.RemoveField(
            model_name='systemaccount',
            name='credits',
        ),
        migrations.RemoveField(
            model_name='systemaccount',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='systemaccount',
            name='debits',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='approver',
        ),
        migrations.DeleteModel(
            name='Account',
        ),
        migrations.DeleteModel(
            name='Currency',
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
        migrations.DeleteModel(
            name='SystemAccount',
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]
