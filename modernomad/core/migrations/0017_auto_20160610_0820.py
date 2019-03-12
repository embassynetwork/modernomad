# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modernomad.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160610_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.ImageField(help_text=b'Images should be 500px x 325px or a 1 to 0.65 ratio ', upload_to=modernomad.core.models.resource_img_upload_to),
        ),
    ]
