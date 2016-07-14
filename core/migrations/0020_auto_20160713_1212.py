# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160610_1027'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original', models.ImageField(null=True, upload_to=core.models.room_img_upload_to, blank=True)),
                ('large', models.ImageField(null=True, upload_to=core.models.room_img_upload_to, blank=True)),
                ('med', models.ImageField(null=True, upload_to=core.models.room_img_upload_to, blank=True)),
                ('thumb', models.ImageField(null=True, upload_to=core.models.room_img_upload_to, blank=True)),
                ('caption', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BookableResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(help_text=b"Optional. Will override (or supplement?) the parent room's description", null=True, blank=True)),
                ('default_rate', models.DecimalField(max_digits=9, decimal_places=2)),
                ('archived', models.BooleanField(default=False, verbose_name=b'Is the resource out of service indefinitely?')),
            ],
        ),
        migrations.RenameField(
            model_name='room',
            old_name='beds',
            new_name='num_beds',
        ),
        migrations.AlterField(
            model_name='reservable',
            name='room',
            field=models.ForeignKey(related_name='reservables', blank=True, to='core.Room', null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='room',
            field=models.ForeignKey(blank=True, to='core.Room', null=True),
        ),
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('bookableresource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.BookableResource')),
                ('room', models.ForeignKey(related_name='beds', to='core.Room')),
            ],
            bases=('core.bookableresource',),
        ),
        migrations.CreateModel(
            name='LocationImage',
            fields=[
                ('baseimage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.BaseImage')),
                ('location', models.ForeignKey(to='core.Location')),
            ],
            bases=('core.baseimage',),
        ),
        migrations.CreateModel(
            name='RoomImage',
            fields=[
                ('baseimage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.BaseImage')),
                ('room', models.ForeignKey(to='core.Room')),
            ],
            bases=('core.baseimage',),
        ),
        migrations.AddField(
            model_name='reservable',
            name='bed',
            field=models.ForeignKey(related_name='reservables', blank=True, to='core.Bed', null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='bed',
            field=models.ForeignKey(blank=True, to='core.Bed', null=True),
        ),
    ]
