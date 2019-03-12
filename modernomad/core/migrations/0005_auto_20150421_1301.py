# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import modernomad.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150413_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitysubscription',
            name='bills',
            field=models.ManyToManyField(to='core.SubscriptionBill'),
        ),
        migrations.AlterField(
            model_name='location',
            name='bank_account_number',
            field=models.IntegerField(help_text=b'We use this to transfer money to you!', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='house_admins',
            field=models.ManyToManyField(related_name='house_admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='image',
            field=models.ImageField(help_text=b'Requires an image with proportions 800px wide x 225px high', upload_to=modernomad.core.models.location_img_upload_to),
        ),
        migrations.AlterField(
            model_name='location',
            name='residents',
            field=models.ManyToManyField(related_name='residences', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='routing_number',
            field=models.IntegerField(help_text=b'We use this to transfer money to you!', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='suppressed_fees',
            field=models.ManyToManyField(to='core.Fee'),
        ),
        migrations.AlterField(
            model_name='room',
            name='residents',
            field=models.ManyToManyField(help_text=b'This field is optional.', related_name='residents', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='roomsubscription',
            name='bills',
            field=models.ManyToManyField(to='core.SubscriptionBill'),
        ),
    ]
