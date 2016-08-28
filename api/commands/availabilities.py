from api.command import *
from datetime import datetime
from core.models import Resource
from django.core.exceptions import ValidationError


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

    def current_date_for_tz(self):
        return datetime.now(self.tz()).date()

    def can_administer_resource(self):
        return user_can_administer_a_resource(self.issuing_user, self.resource())

    def _validate_not_in_past(self):
        if self.start_date() < self.current_date_for_tz():
            self.add_error('start_date', u'The start date must not be in the past')

    def _resource_availabilities(self, order='start_date'):
        return Availability.objects.filter(resource=self.resource()).order_by(order)

    def _next_availability(self):
        return self._resource_availabilities('start_date').filter(start_date__gt=self.start_date()).first()

    def _previous_availability(self):
        return self._resource_availabilities('-start_date').filter(start_date__lt=self.start_date()).first()


class SerializedAvailabilityCommand(SerializedModelCommand):
    def _model_class(self):
        return AvailabilitySerializer

    def resource(self):
        return self.validated_data('resource')

    def start_date(self):
        return self.validated_data('start_date')


class UpdateOrAddAvailabilityChange(DecoratorCommand, AvailabilityCommandHelpers):
    def _determine_inner(self):
        existing = self._fetch_existing_availability_for_date(self.start_date())
        if existing:
            self.inner_command = UpdateAvailabilityChange(self.issuing_user, availability=existing, quantity=self.input_data.get('quantity'))
        else:
            self.inner_command = AddAvailabilityChange(self.issuing_user, **self.input_data)

    def resource(self):
        return Resource.objects.get(pk=self.input_data['resource'])

    def start_date(self):
        date_string = self.input_data.get('start_date')
        if date_string:
            return datetime.strptime(date_string, "%Y-%m-%d").date()

    def _fetch_existing_availability_for_date(self, start_date):
        return self._resource_availabilities().filter(start_date=start_date).first()


class UpdateAvailabilityChange(ModelCommand, AvailabilityCommandHelpers):
    def _check_if_valid(self):
        self.model().quantity = self.input_data['quantity']

        self._validate_not_in_past()
        self._is_model_valid()

        return not self.has_errors()

    def model(self):
        return self.input_data['availability']

    def resource(self):
        return self.model().resource

    def start_date(self):
        return self.model().start_date

    def _serialize_model(self):
        return AvailabilitySerializer(self.model()).data


class AddAvailabilityChange(SerializedAvailabilityCommand, AvailabilityCommandHelpers):
    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False

        if not self.can_administer_resource():
            return self.unauthorized()

        self._validate_not_in_past()

        return not self.has_errors()

    def _execute_on_valid(self):
        if self._would_not_change_previous_quantity():
            self.add_warning('quantity', u'This is not a change from the previous availability')
            return
        if self._same_as_next_quantity():
            self.add_warning('quantity', u'The availability change was combined with the one following it, which was the same.')
            self._delete_next_quantity()

        self._save_deserialized_model()

    def _would_not_change_previous_quantity(self):
        return self._previous_quantity() == self.validated_data('quantity')

    def _delete_next_quantity(self):
        self._next_availability().delete()

    def _same_as_next_quantity(self):
        return self._next_quantity() == self.validated_data('quantity')

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

        self._validate_not_in_past()

        return not self.has_errors()

    def _execute_on_valid(self):
        to_delete = self._to_delete()
        keys = [record.pk for record in to_delete]
        for record in to_delete:
            record.delete()

        self.result_data = {'deleted': {'availabilities': keys}}

    def _to_delete(self):
        result = [self.availability()]
        next_avail = self._next_availability()

        if next_avail:
            previous_avail = self._previous_availability()
            if (previous_avail and previous_avail.quantity == next_avail.quantity):
                result.append(next_avail)
        return result
