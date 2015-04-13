# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_subscriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitysubscription',
            name='bills',
            field=models.ManyToManyField(to='core.SubscriptionBill', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='roomsubscription',
            name='bills',
            field=models.ManyToManyField(to='core.SubscriptionBill', null=True, blank=True),
            preserve_default=True,
        ),
    ]
