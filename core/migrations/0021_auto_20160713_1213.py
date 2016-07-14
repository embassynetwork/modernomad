# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_resources(apps, schema_editor):
	Room = apps.get_model("core", "Room")
	Bed = apps.get_model("core", "Bed")
	Reservable = apps.get_model("core", "Reservable")

	all_rooms = Room.objects.all()
	for room in all_rooms:
		reservables = room.reservables.all()
		num_beds = room.num_beds
		for bed in range(num_beds):
			# create the right number of bed objects
			b = Bed()
			b.room = room
			b.default_rate = room.default_rate
			b.save()
			# create reservables that match the dates of the reservables on
			# the room 
			for room_reservable in reservables:
				new_reservable = Reservable(room=room, bed=b, start_date=room_reservable.start_date, end_date=room_reservable.end_date)
				new_reservable.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20160713_1212'),
    ]

    operations = [
		migrations.RunPython(add_resources),
    ]
