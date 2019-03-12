from modernomad.core.models import CapacityChange
from modernomad.core.serializers import CapacityChangeSerializer


class ResourceCapacity:
    def __init__(self, resource, date):
        self.resource = resource
        self.date = date

    def resource_id(self):
        return self.resource.id

    def current_capacity(self):
        return self.base_scope().filter(start_date__lte=self.date).order_by('-start_date').first()

    def upcoming_capacities(self):
        return list(self.base_scope().filter(start_date__gt=self.date).order_by('start_date'))

    def base_scope(self):
        return CapacityChange.objects.filter(resource=self.resource)


class SerializedNullResourceCapacity:
    def as_dict(self):
        return {
            'resourceId': None,
            'currentCapacity': None,
            'upcomingCapacities': []
        }

class SerializedResourceCapacity:
    def __init__(self, resource, date):
        self.resource_capacity = ResourceCapacity(resource, date)

    def current_capacity(self):
        record = self.resource_capacity.current_capacity()
        return self._serializeRecord(record)

    def upcoming_capacities(self):
        capacities = self.resource_capacity.upcoming_capacities()
        return list(map(self._serializeRecord, capacities))

    def as_dict(self):
        return {
            'resourceId': self.resource_capacity.resource_id(),
            'currentCapacity': self.current_capacity(),
            'upcomingCapacities': self.upcoming_capacities()
        }

    def _serializeRecord(self, record):
        return CapacityChangeSerializer(record).data if record else None
