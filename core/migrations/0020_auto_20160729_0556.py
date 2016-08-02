# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160610_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='profile_image',
            field=models.ImageField(help_text=b'A shiny high profile image for the location', null=True, upload_to=core.models.location_img_upload_to, blank=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
