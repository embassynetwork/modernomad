from api.command import *
from datetime import datetime
from django.core.exceptions import ValidationError
from modernomad.core.models import Resource
from modernomad.core.models import CapacityChange

def user_can_administer_a_resource(user, resource):
    return (
        user and
        resource and
        resource.location and
        (
            user in resource.backers()
            or
            user in resource.location.house_admins.all()
        )
    )

def in_the_past(capacity):
    tz = capacity.resource.tz()
    now = datetime.now(tz).date()
    return capacity.start_date < now

def get_or_create_unsaved_capacity(data):
    # if there is an existing capacity change for this date, then we're updating. otherwise we're adding.
    capacity = CapacityChange.objects.filter(start_date=data['start_date'], resource=data['resource']).first()
    if capacity:
        capacity.quantity = data['quantity']
        capacity.accept_drft = data['accept_drft']
    else:
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        capacity = CapacityChange(
                start_date=start_date,
                resource=Resource.objects.get(id=data['resource']),
                accept_drft=data['accept_drft'],
                quantity=data['quantity']
            )
    return capacity

def update_capacities_as_appropriate(capacity):
    ''' checks various policiies about neighboring capacities and updates (or
    not) as appropriate.'''
    warnings = {}
    errors = {}
    if in_the_past(capacity):
        errors['start_date'] = u'The start date must not be in the past'

    elif CapacityChange.objects.would_not_change_previous_quantity(capacity):
        warnings['Oops'] = u'This is not a change from the previous capacity'

    elif CapacityChange.objects.same_as_next_quantity(capacity):
        CapacityChange.objects.delete_next_quantity(capacity)
        capacity.save()
        warnings['FYI'] = u'The capacity change was combined with the one following it, which was the same.'

    else:
        capacity.save()

    return (errors, warnings)

class CapacityCommandHelpers:
    def tz(self):
        return self.resource().tz()

    def current_date_for_tz(self):
        return datetime.now(self.tz()).date()

    def can_administer_resource(self):
        return user_can_administer_a_resource(self.issuing_user, self.resource())

    def _validate_not_in_past(self):
        if self.start_date() < self.current_date_for_tz():
            self.add_error('start_date', u'The start date must not be in the past')

class DeleteCapacityChange(Command, CapacityCommandHelpers):
    ''' this is being used in views/capacities.py.'''
    def capacity(self):
        return self.input_data['capacity']

    def start_date(self):
        return self.capacity().start_date

    def resource(self):
        return self.capacity().resource

    def _check_if_valid(self):
        if not self.can_administer_resource():
            return self.unauthorized()

        self._validate_not_in_past()

        return not self.has_errors()

    def _execute_on_valid(self):
        to_delete = self._to_delete()
        keys = [record.pk for record in to_delete]
        for record in to_delete:
            record.delete()

        self.result_data = {'deleted': {'capacities': keys}}

    def _to_delete(self):
        result = [self.capacity()]
        next_avail = CapacityChange.objects._next_capacity(self.capacity())

        if next_avail:
            previous_avail = CapacityChange.objects._previous_capacity(self.capacity())
            if (previous_avail and previous_avail.quantity == next_avail.quantity):
                result.append(next_avail)
        return result
