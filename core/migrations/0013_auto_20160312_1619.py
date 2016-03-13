# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20160312_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='context',
            field=models.CharField(max_length=32, choices=[(b'reservation', b'Reservation'), (b'subscription', b'Subscription')]),
        ),
    ]
