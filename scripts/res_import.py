from django.utils import timezone
from django.contrib.auth.models import User, Group
from core.models import Location, Booking, Payment, Room
from datetime import datetime
import json

'''
Usage
./manage shell
import res_import
res_import.import_bookings("farmhouse_bookings.json", "farmhouse_payments.json", 3, 28)
'''
def import_bookings(booking_file, payment_file, location_id, room_offset):
	json_file = open(booking_file)
	booking_data = json.load(json_file)
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
	        "booking": 3,
	        "payment_service": "Stripe",
	        "transaction_id": "ch_103svy24GAclB9sbIZjFL5LY"
	    }
	}
	'''
	payments_by_booking = {}
	for p in payment_data:
		payment = p['fields']
		payment_id = p['pk']
		if 'booking' in payment:
			booking_id = payment['booking']
			payments_by_booking[booking_id] = payment
		else:
			print "payment %s has no booking!" % payment_id
	#print payments_by_booking
	
	'''
	{
	    "pk": 1,
	    "model": "core.booking",
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
	for r in booking_data:
		old_booking = r['fields']
		old_booking_id = r['pk']
		
		old_room_id = old_booking['room']
		new_room_id = int(old_room_id) + room_offset
		print "old_booking_id = %s, old_room_id = %s, new_room_id = %s" % (old_booking_id, old_room_id, new_room_id)
		new_room = Room.objects.get(id=new_room_id)
		#print "room = %s" % new_room.name
		username = r['fields']['user'][0]
		user = User.objects.filter(username=username).first()

		new_booking = Booking(status=old_booking['status'],
			updated=old_booking['updated'],
			depart=old_booking['depart'],
			last_msg=old_booking['last_msg'],
			created=old_booking['created'],
			purpose=old_booking['purpose'],
			tags=old_booking['tags'],
			comments=old_booking['comments'],
			rate=old_booking['rate'],
			arrive=old_booking['arrive'],
			user=user,
			location=location,
			room=new_room,
		)
		new_booking.save()
		#print new_booking

		# Now create the payment for this new booking
		if old_booking_id in payments_by_booking:
			old_payment = payments_by_booking[old_booking_id]
			print "booking %s has payment of $%s" % (old_booking_id, old_payment['paid_amount'])
			new_payment = Payment(payment_method=old_payment['payment_method'],
				payment_service=old_payment['payment_service'],
				transaction_id=old_payment['transaction_id'],
				paid_amount=old_payment['paid_amount'],
				booking=new_booking,
			)
			new_payment.save()
			new_payment.payment_date = old_payment['payment_date']
			new_payment.save()

		# Pull the booking back out of the DB and recalculate the bill
		pulled_booking = Booking.objects.get(id=new_booking.id)
		pulled_booking.generate_bill()