# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import modernomad.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20160609_0335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(help_text=b'Displayed on room detail page only', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.ImageField(help_text=b'Images should be 500px x 325px or a 1 to 0.65 ratio ', upload_to=modernomad.core.models.resource_img_upload_to, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='residents',
            field=models.ManyToManyField(help_text=b'Residents have the ability to edit the room and its reservable data ranges. Adding multiple people will give them all permission to edit the room. If a user removes themselves, they will no longer be able to edit the room.', related_name='rooms', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='summary',
            field=models.CharField(default=b'', help_text=b'Displayed on the search page. Max length 140 chars', max_length=140),
        ),
    ]
