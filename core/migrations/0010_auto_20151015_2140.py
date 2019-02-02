# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forward(apps, schema_editor):
    Room = apps.get_model("core", "Room")
    rooms = Room.objects.all()
    for r in rooms:
        r.summary = r.description[0:140]
        r.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20151015_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='summary',
            field=models.CharField(max_length=140, help_text=b'Max length 140 chars', default=''),
        ),
        migrations.RunPython(forward, elidable=True),
    ]
