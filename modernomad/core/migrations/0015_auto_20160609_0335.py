# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160416_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='residents',
            field=models.ManyToManyField(help_text=b'This field is optional.', related_name='rooms', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
