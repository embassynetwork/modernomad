from core.models import Availability

class RoomAvailability:
	def __init__(self, room, date):
		self.room = room
		self.date = date

	def current_availability(self):
		return self.base_scope().filter(start_date__lte=self.date).order_by('-start_date').first()

	def upcoming_availabilities(self):
		return list(self.base_scope().filter(start_date__gt=self.date).order_by('start_date'))

	def base_scope(self):
		return Availability.objects.filter(resource=self.room)

class SerializedRoomAvailability:
    def __init__(self, room, date):
        self.room_availability = RoomAvailability(room, date)

    def current_availability(self):
        record = self.room_availability.current_availability()
        return self.__serializeRecord(record)

    def upcoming_availabilities(self):
        availabilities = self.room_availability.upcoming_availabilities()
        return map(self.__serializeRecord, availabilities)

    def __serializeRecord(self, record):
        return record.toDict() if record else None
