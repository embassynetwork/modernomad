# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160921_0237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookingnote',
            old_name='reservation',
            new_name='booking',
        ),
        migrations.AlterField(
            model_name='bookingnote',
            name='booking',
            field=models.ForeignKey(related_name='booking_note', null=False, to='core.Booking'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='bill',
            field=models.OneToOneField(related_name='booking', null=True, to='core.BookingBill'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='location',
            field=models.ForeignKey(related_name='bookings', to='core.Location', null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
