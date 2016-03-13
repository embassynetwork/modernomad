# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_subscriptions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptionbill',
            options={'ordering': ['-period_start']},
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='context',
            field=models.CharField(default='reservation', max_length=32, choices=[(b'Reservation', b'reservation'), (b'Subscription', b'subscription')]),
            preserve_default=False,
        ),
    ]
