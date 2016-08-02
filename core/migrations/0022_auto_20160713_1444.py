# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from datetime import timedelta, date

from django.db import models, migrations

def get_overlapping_in_room(Reservation, reservation):
	''' FYI, we don't care if canceled or pending reservations overlap.'''
	overlapping = []
	# get reservations of any status, but exclude the one being queried against. 
	try:
		reservations_this_room = Reservation.objects.filter(room=reservation.bed.room) 
	except:
		reservations_this_room = Reservation.objects.filter(room=reservation.room) 
	before_or_around = reservations_this_room.filter(arrive__lt=reservation.arrive, depart__gt=reservation.arrive).exclude(id=reservation.id).filter(Q(status="confirmed") | Q(status="approved")) 
	between_or_after = reservations_this_room.filter(arrive__gte=reservation.arrive).filter(arrive__lt=reservation.depart).exclude(id=reservation.id).filter(Q(status="confirmed") | Q(status="approved"))
	return list(before_or_around) + list(between_or_after)

def get_free_beds_on_dates_or_none(Reservation, room, arrive, depart):
	beds = room.beds.all()
	free = []
	for b in beds:
		if is_free_between(Reservation, b, arrive, depart):
			free.append(b)
	return free

def is_reservable_this_day(bed, this_day):
	# there *should* never be more than 1 reservable on a given day... 
	try:
		reservable_today = bed.reservables.filter(bed=bed).filter(start_date__lte=this_day).get(Q(end_date__gte=this_day) | Q(end_date=None))  
	except:
		reservable_today = False
	return bool(reservable_today)

def is_free_this_day(Reservation, bed, this_day):
	# must a. be reservable, and b. not have any other reservations. 
	if not is_reservable_this_day(bed, this_day):
		return False
	booked = Reservation.objects.filter(bed=bed, arrive__lte=this_day).filter(depart__gt=this_day).filter(Q(status="confirmed") | Q(status="approved"))
	if booked:
		return False
	else:
		return True

def is_free_between(Reservation, bed, arrive, depart):
	# must a. be reservable, and b. not have any other reservations. 
	day = arrive
	while day < depart:
		if is_free_this_day(Reservation, bed, day):
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
		print '\nmigrating reservation %d' % res.id
		overlapping = get_overlapping_in_room(Reservation, res)
		if not res.bed or len(overlapping)>0:
			''' in case there is a reservation that already has a bed, there is nothing to migrate.'''
			free_beds = get_free_beds_on_dates_or_none(Reservation, res.room, res.arrive, res.depart)
			if free_beds:
				b = free_beds[0]
			else:
				b = res.room.beds.first()
				possible_conflicts.append(res)
			res.bed = b
			res.save()

	for res in all_reservations:
		if not res.room == res.bed.room:
			print "warning! reservation %d: original reservation room %s does not match new bed object's room %s." % (res.id, res.room, res.bed.room.name)
	
	print 'possible conflicts noted:'
	print len(possible_conflicts)



class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20160713_1213'),
    ]

    operations = [
		migrations.RunPython(migrate_reservations),
    ]
