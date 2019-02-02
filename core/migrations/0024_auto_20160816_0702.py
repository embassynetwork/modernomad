# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def migrate_reservables(apps, schema_editor):
    Resource = apps.get_model('core', 'Resource')
    Availability = apps.get_model('core', 'Availability')
    Reservable = apps.get_model('core', 'Reservable')

    reservables = Reservable.objects.all()
    for reservable in reservables:
        if not Availability.objects.filter(start_date=reservable.start_date, resource=reservable.resource):
            availability = Availability(start_date=reservable.start_date, resource=reservable.resource, quantity=reservable.resource.beds)
        availability.save()

    for reservable in reservables:
        if reservable.end_date:
            if not Availability.objects.filter(start_date=reservable.end_date, resource=reservable.resource):
                availability = Availability(start_date=reservable.end_date, resource=reservable.resource, quantity=0)
                availability.save()

def reverse_migrate_reservables(apps, schema_editor):
    Availability = apps.get_model('core', 'Availability')
    Availability.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160808_0330'),
    ]

    operations = [
        migrations.RunPython(migrate_reservables, reverse_migrate_reservables, elidable=True)
    ]
