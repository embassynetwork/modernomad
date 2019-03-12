# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def migrate_fields_from_booking_to_use(apps, schema_editor):
    Booking = apps.get_model('core', 'Booking')
    Use = apps.get_model('core', 'Use')

    bookings = Booking.objects.all()
    for b in bookings:
        ''' migrate fields location, status, user, arrive, depart,
        arrival_time, resource, purpose, last_msg.'''
        use = Use(location = b.location, 
                status = b.status,
                user = b.user, 
                arrive = b.arrive, 
                depart  = b.depart, 
                arrival_time = b.arrival_time, 
                resource = b.resource, 
                purpose = b.purpose, 
                last_msg  = b.last_msg)
        use.save()
        b.use = use
        b.save()


def reverse_migrate_fields_from_booking_to_use(apps, schema_editor):

    Booking = apps.get_model('core', 'Booking')
    Use = apps.get_model('core', 'Use')
    uses = Use.objects.all()
    for u in uses:
        ''' migrate fields back to booking: location, status, user, arrive,
        depart, arrival_time, resource, purpose, last_msg.'''
        b = u.booking

        b.location = u.location
        b.status = u.status
        b.user = b.use
        b.arrive = b.arrive
        b.depart  = b.depart
        b.arrival_time = b.arrival_time
        b.resource = b.resource
        b.purpose = b.purpose
        b.last_msg  = b.last_msg

        b.save()

    Use.objects.all().delete()
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20160922_0303'),
    ]

    operations = [
        migrations.RunPython(migrate_fields_from_booking_to_use, reverse_migrate_fields_from_booking_to_use, elidable=True)
    ]
