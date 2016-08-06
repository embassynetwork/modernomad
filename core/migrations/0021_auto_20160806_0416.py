# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import core.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0020_auto_20160729_0556'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('default_rate', models.DecimalField(max_digits=9, decimal_places=2)),
                ('description', models.TextField(help_text=b'Displayed on room detail page only', null=True, blank=True)),
                ('summary', models.CharField(default=b'', help_text=b'Displayed on the search page. Max length 140 chars', max_length=140)),
                ('cancellation_policy', models.CharField(default=b'24 hours', max_length=400)),
                ('shared', models.BooleanField(default=False, verbose_name=b'Is this a hostel/shared accommodation room?')),
                ('beds', models.IntegerField()),
                ('image', models.ImageField(help_text=b'Images should be 500px x 325px or a 1 to 0.65 ratio ', upload_to=core.models.resource_img_upload_to)),
                ('location', models.ForeignKey(related_name='resources', to='core.Location', null=True)),
                ('residents', models.ManyToManyField(help_text=b'Residents have the ability to edit the room and its reservable data ranges. Adding multiple people will give them all permission to edit the room. If a user removes themselves, they will no longer be able to edit the room.', related_name='resources', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='room',
            name='location',
        ),
        migrations.RemoveField(
            model_name='room',
            name='residents',
        ),
        migrations.RemoveField(
            model_name='reservable',
            name='room',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='room',
        ),
        migrations.RemoveField(
            model_name='roomimage',
            name='room',
        ),
        migrations.DeleteModel(
            name='Room',
        ),
        migrations.AddField(
            model_name='reservable',
            name='resource',
            field=models.ForeignKey(related_name='reservables', default=-1, to='core.Resource'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='resource',
            field=models.ForeignKey(to='core.Resource', null=True),
        ),
        migrations.AddField(
            model_name='roomimage',
            name='resource',
            field=models.ForeignKey(default=-1, to='core.Resource'),
            preserve_default=False,
        ),
    ]
