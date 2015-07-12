# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150505_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(help_text=b'In what city are you primarily based?', max_length=200, verbose_name=b'City'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='referral',
            field=models.CharField(help_text=b'How did you hear about us? (Give a name if possible!)', max_length=200),
        ),
    ]
