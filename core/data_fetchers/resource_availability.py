from core.models import Availability

class ResourceAvailability:
    def __init__(self, resource, date):
        self.resource = resource
        self.date = date

    def current_availability(self):
        return self.base_scope().filter(start_date__lte=self.date).order_by('-start_date').first()

    def upcoming_availabilities(self):
        return list(self.base_scope().filter(start_date__gt=self.date).order_by('start_date'))

    def base_scope(self):
        return Availability.objects.filter(resource=self.resource)

class SerializedNullResourceAvailability:
    def as_dict(self):
        return {
            'currentAvailability': None,
            'upcomingAvailabilities': []
        }

class SerializedResourceAvailability:
    def __init__(self, resource, date):
        self.resource_availability = ResourceAvailability(resource, date)

    def current_availability(self):
        record = self.resource_availability.current_availability()
        return self.__serializeRecord(record)

    def upcoming_availabilities(self):
        availabilities = self.resource_availability.upcoming_availabilities()
        return map(self.__serializeRecord, availabilities)

    def as_dict(self):
        return {
            'currentAvailability': self.current_availability(),
            'upcomingAvailabilities': self.upcoming_availabilities()
        }

    def __serializeRecord(self, record):
        return record.toDict() if record else None
