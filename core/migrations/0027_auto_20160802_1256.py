# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservable',
            name='room',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='room',
        ),
        migrations.AlterField(
            model_name='bookableresource',
            name='description',
            field=models.TextField(help_text=b'Optional supplemental description.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='reservable',
            name='end_date',
            field=models.DateField(help_text=b'Leave this blank for a room with open ended availability.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.ImageField(upload_to=core.models.room_img_upload_to),
        ),
    ]
