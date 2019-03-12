# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import modernomad.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160610_1027'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original', models.ImageField(null=True, upload_to=modernomad.core.models.resource_img_upload_to, blank=True)),
                ('large', models.ImageField(null=True, upload_to=modernomad.core.models.resource_img_upload_to, blank=True)),
                ('med', models.ImageField(null=True, upload_to=modernomad.core.models.resource_img_upload_to, blank=True)),
                ('thumb', models.ImageField(null=True, upload_to=modernomad.core.models.resource_img_upload_to, blank=True)),
                ('caption', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='profile_image',
            field=models.ImageField(help_text=b'A shiny high profile image for the location', null=True, upload_to=modernomad.core.models.location_img_upload_to, blank=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
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
    ]
