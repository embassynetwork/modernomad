# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20160922_0519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usenote',
            name='booking_deprecated',
            field=models.ForeignKey(related_name='booking_notes', blank=True, to='core.Booking', null=True),
        ),
        migrations.AlterField(
            model_name='usenote',
            name='use',
            field=models.ForeignKey(related_name='use_notes', to='core.Use'),
        ),
    ]
