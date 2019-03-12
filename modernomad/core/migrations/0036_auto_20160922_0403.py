# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def migrate_field(apps, schema_editor):
    BookingNote = apps.get_model('core', 'BookingNote')
    notes = BookingNote.objects.all()
    for note in notes:
        note.use = note.booking.use
        note.save()

def reverse_migrate_field(apps, schema_editor):
    BookingNote = apps.get_model('core', 'BookingNote')
    notes = BookingNote.objects.all()
    for note in notes:
        note.booking = note.use.booking
        note.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_bookingnote_use'),
    ]

    operations = [
        migrations.RunPython(migrate_field, reverse_migrate_field, elidable=True)
    ]
