# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160713_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookableresource',
            name='name',
            field=models.CharField(default='A bed', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='location',
            name='stay_page',
            field=models.TextField(default=b'This is the page which has some descriptive text at the top (this text), and then lists the available rooms and beds. HTML is supported.'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='bed',
            field=models.ForeignKey(related_name='reservations', blank=True, to='core.Bed', null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='room',
            field=models.ForeignKey(related_name='reservations', blank=True, to='core.Room', null=True),
        ),
    ]
