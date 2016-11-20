# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bank', '0003_auto_20161118_1111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='owner',
        ),
        migrations.AddField(
            model_name='account',
            name='name',
            field=models.CharField(help_text=b'Give this account a nickname (optional)', max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='account',
            name='owners',
            field=models.ManyToManyField(help_text=b'May be blank for group accounts', related_name='accounts_owned', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
