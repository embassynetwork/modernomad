# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# this are all methods on Room model, but for some reason, maybe to do with the
# comment here (https://docs.djangoproject.com/en/1.9/topics/migrations/) about
# accessing 'old versions' of apps (?) we can't access it. so redefining it
# here. 
def get_free_beds_on_dates_or_none(room, arrive, depart):
	beds = room.beds.all()
	free = []
	for b in beds:
		if is_free_between(b, arrive, depart):
			free.append(b)
	return free

def is_reservable_this_day(bed, this_day):
	# there *should* never be more than 1 reservable on a given day... 
	try:
		reservable_today = bed.reservables.filter(bed=self).filter(start_date__lte=this_day).get(Q(end_date__gte=this_day) | Q(end_date=None))  
	except:
		reservable_today = False
	return bool(reservable_today)

def is_free_this_day(bed, this_day):
	# must a. be reservable, and b. not have any other reservations. 
	if not is_reservable_this_day(bed, this_day):
		return False
	booked = bed.reservations.filter(arrive__lte=this_day).filter(depart__gte=this_day)
	if booked:
		return False
	else:
		return True

def is_free_between(bed, arrive, depart):
	# must a. be reservable, and b. not have any other reservations. 
	day = arrive
	while day < depart:
		if is_free_this_day(bed, day):
			day = day + timedelta(days=1)
		else:
			return False
	return True


def migrate_reservations(apps, schema_editor):
	Room = apps.get_model("core", "Room")
	Bed = apps.get_model("core", "Bed")
	Reservation = apps.get_model("core", "Reservation")

	all_reservations = Reservation.objects.all()
	possible_conflicts = []
	for res in all_reservations:
		free_beds = get_free_beds_on_dates_or_none(res.room, res.arrive, res.depart)
		if free_beds:
			b = free_beds[0]
		else:
			b = res.room.beds.first()
			possible_conflicts.append(res)
		res.bed = b
		res.save()

	for res in all_reservations:
		if not res.room == res.bed.room:
			print "warning! reservation %d: bed %s is not in original reservation room %s." % (res.id, res.room, res.bed.room.name)
	
	print 'possible conflicts noted:'
	print possible_conflicts



class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20160713_1213'),
    ]

    operations = [
		migrations.RunPython(migrate_reservations),
    ]
