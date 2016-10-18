# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20160921_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingnote',
            name='booking',
            field=models.ForeignKey(related_name='booking_notes', to='core.Booking'),
        ),
    ]
