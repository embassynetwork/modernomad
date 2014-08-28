from django.utils import timezone
from django.contrib.auth.models import User, Group
from core.models import Location, Reservation, Payment, Room
from datetime import datetime
import json

'''
Usage
./manage shell
import res_import
res_import.import_reservations("farmhouse_reservations.json", "farmhouse_payments.json", 3, 28)
'''
def import_reservations(reservation_file, payment_file, location_id, room_offset):
	json_file = open(reservation_file)
	reservation_data = json.load(json_file)
	json_file.close()
	
	json_file = open(payment_file)
	payment_data = json.load(json_file)
	json_file.close()
	
	location = Location.objects.get(pk=location_id)
	print "location=%s" % location.name
	
	'''
	{
	    "pk": 3,
	    "model": "core.payment",
	    "fields": {
	        "automatic_invoice": false,
	        "payment_date": "2014-04-20T01:45:29.635Z",
	        "paid_amount": "225",
	        "payment_method": "Visa",
	        "reservation": 3,
	        "payment_service": "Stripe",
	        "transaction_id": "ch_103svy24GAclB9sbIZjFL5LY"
	    }
	}
	'''
	payments_by_reservation = {}
	for p in payment_data:
		payment = p['fields']
		payment_id = p['pk']
		if 'reservation' in payment:
			reservation_id = payment['reservation']
			payments_by_reservation[reservation_id] = payment
		else:
			print "payment %s has no reservation!" % payment_id
	#print payments_by_reservation
	
	'''
	{
	    "pk": 1,
	    "model": "core.reservation",
	    "fields": {
	        "status": "canceled",
	        "updated": "2014-08-26T22:46:47.303Z",
	        "depart": "2014-04-05",
	        "room": 1,
	        "last_msg": "2014-04-02T20:40:06.221Z",
	        "created": "2014-04-02T20:34:16.979Z",
	        "purpose": "kdjkj",
	        "tags": "",
	        "comments": "",
	        "arrival_time": "",
	        "rate": 75,
	        "user": [
	            "meganlipsett"
	        ],
	        "arrive": "2014-04-02",
	        "location": 1
	    }
	},
	'''
	for r in reservation_data:
		old_reservation = r['fields']
		old_reservation_id = r['pk']
		
		old_room_id = old_reservation['room']
		new_room_id = int(old_room_id) + room_offset
		print "old_reservation_id = %s, old_room_id = %s, new_room_id = %s" % (old_reservation_id, old_room_id, new_room_id)
		new_room = Room.objects.get(id=new_room_id)
		#print "room = %s" % new_room.name
		username = r['fields']['user'][0]
		user = User.objects.filter(username=username).first()

		new_reservation = Reservation(status=old_reservation['status'],
			updated=old_reservation['updated'],
			depart=old_reservation['depart'],
			last_msg=old_reservation['last_msg'],
			created=old_reservation['created'],
			purpose=old_reservation['purpose'],
			tags=old_reservation['tags'],
			comments=old_reservation['comments'],
			rate=old_reservation['rate'],
			arrive=old_reservation['arrive'],
			user=user,
			location=location,
			room=new_room,
		)
		new_reservation.save()
		#print new_reservation

		# Now create the payment for this new reservation
		if old_reservation_id in payments_by_reservation:
			old_payment = payments_by_reservation[old_reservation_id]
			print "reservation %s has payment of $%s" % (old_reservation_id, old_payment['paid_amount'])
			new_payment = Payment(payment_method=old_payment['payment_method'],
				payment_service=old_payment['payment_service'],
				transaction_id=old_payment['transaction_id'],
				paid_amount=old_payment['paid_amount'],
				reservation=new_reservation,
			)
			new_payment.save()
			new_payment.payment_date = old_payment['payment_date']
			new_payment.save()

		# Pull the reservation back out of the DB and recalculate the bill
		pulled_reservation = Reservation.objects.get(id=new_reservation.id)
		pulled_reservation.generate_bill()