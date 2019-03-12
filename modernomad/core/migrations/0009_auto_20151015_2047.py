# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modernomad.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_payment_last4'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last4',
            field=models.IntegerField(help_text=b"Last 4 digits of the user's card on file, if any", null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(help_text=b'Max length 140 chars', max_length=140, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.ImageField(help_text=b'Images should be 500px x 325px or a 1 to 0.65 ratio ', null=True, upload_to=modernomad.core.models.resource_img_upload_to, blank=True),
        ),
    ]
