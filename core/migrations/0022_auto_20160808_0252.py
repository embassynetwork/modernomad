# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20160806_0416'),
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField()),
                ('number', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='resource',
            name='location',
            field=models.ForeignKey(related_name='resources', to='core.Location', null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='residents',
            field=models.ManyToManyField(help_text=b'Residents have the ability to edit the room and its reservable data ranges. Adding multiple people will give them all permission to edit the room. If a user removes themselves, they will no longer be able to edit the room.', related_name='resources', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='availability',
            name='resource',
            field=models.ForeignKey(to='core.Resource'),
        ),
    ]
