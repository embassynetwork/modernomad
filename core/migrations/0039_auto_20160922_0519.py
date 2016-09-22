# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20160922_0408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='arrive_deprecated',
            field=models.DateField(null=True, verbose_name=b'Arrival Date'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='depart_deprecated',
            field=models.DateField(null=True, verbose_name=b'Departure Date'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='purpose_deprecated',
            field=models.TextField(null=True, verbose_name=b'Tell us a bit about the reason for your trip/stay'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status_deprecated',
            field=models.CharField(default=b'pending', max_length=200, null=True, blank=True, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'confirmed', b'Confirmed'), (b'house declined', b'House Declined'), (b'user declined', b'User Declined'), (b'canceled', b'Canceled')]),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user_deprecated',
            field=models.ForeignKey(related_name='bookings', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
