from api.command import *
from datetime import datetime


def user_can_administer_a_resource(user, resource):
    return (
        user and
        resource and
        resource.location and
        user in resource.location.house_admins.all()
    )


class AvailabilityCommandHelpers:
    def tz(self):
        return self.resource().tz()

    def can_administer_resource(self):
        return user_can_administer_a_resource(self.issuing_user, self.resource())


class AddAvailabilityChange(ModelCreationBaseCommand, AvailabilityCommandHelpers):
    def _model_class(self):
        return AvailabilitySerializer

    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False

        if not self.can_administer_resource():
            return self.unauthorized()

        if self.start_date() < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self.has_errors()

    def _execute_on_valid(self):
        if self._would_not_change_previous_quantity():
            self.add_warning('quantity', u'This is not a change from the previous availability')
            return
        if self._same_as_next_quantity():
            self.add_warning('quantity', u'The availability change was combined with the one following it, which was the same.')
            self._delete_next_quantity()

        self._save_deserialized_model()

    def resource(self):
        return self.validated_data('resource')

    def start_date(self):
        return self.validated_data('start_date')

    def _would_not_change_previous_quantity(self):
        return self._previous_quantity() == self.validated_data('quantity')

    def _delete_next_quantity(self):
        self._next_availability().delete()

    def _same_as_next_quantity(self):
        return self._next_quantity() == self.validated_data('quantity')

    def _next_availability(self):
        return Availability.objects.filter(start_date__gt=self.start_date(), resource=self.resource()) \
                           .order_by('start_date').first()

    def _next_quantity(self):
        availability = self._next_availability()
        return availability.quantity if availability else None

    def _previous_quantity(self):
        return Availability.objects.quantity_on(self.start_date(), self.resource())


class DeleteAvailabilityChange(Command, AvailabilityCommandHelpers):
    def availability(self):
        return self.input_data['availability']

    def start_date(self):
        return self.availability().start_date

    def resource(self):
        return self.availability().resource

    def _check_if_valid(self):
        if not self.can_administer_resource():
            return self.unauthorized()

        if self.start_date() < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self.has_errors()

    def _execute_on_valid(self):
        to_delete = self._to_delete()
        keys = [record.pk for record in to_delete]
        for record in to_delete:
            record.delete()

        self.result_data = {'deleted': {'availabilities': keys}}

    def _resource_availabilities(self, order='start_date'):
        return Availability.objects.filter(resource=self.resource()).order_by(order)

    def _next_availability(self):
        return self._resource_availabilities('start_date').filter(start_date__gt=self.start_date()).first()

    def _previous_availability(self):
        return self._resource_availabilities('-start_date').filter(start_date__lt=self.start_date()).first()

    def _to_delete(self):
        result = [self.availability()]
        next_avail = self._next_availability()

        if next_avail:
            previous_avail = self._previous_availability()
            if (previous_avail and previous_avail.quantity == next_avail.quantity):
                result.append(next_avail)
        return result
