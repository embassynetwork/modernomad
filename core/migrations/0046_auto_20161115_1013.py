# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20161115_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='admins',
            field=models.ManyToManyField(related_name='accounts_administered', to=settings.AUTH_USER_MODEL),
        ),
    ]
