# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20160302_0919'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communitysubscription',
            name='recurring_charge_date',
        ),
        migrations.RemoveField(
            model_name='roomsubscription',
            name='recurring_charge_date',
        ),
    ]
