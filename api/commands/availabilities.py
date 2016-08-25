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

        if self.validated_data('start_date') < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self.has_errors()

    def _execute_on_valid(self):
        if self._would_not_change_quantity():
            self.add_warning('quantity', u'This is not a change from the previous availability')
            return

        self._save_deserialized_model()

    def resource(self):
        return self.validated_data('resource')

    def _would_not_change_quantity(self):
        return self._previous_quantity() == self.validated_data('quantity')

    def _previous_quantity(self):
        return Availability.objects.quantity_on(self.validated_data('start_date'), self.validated_data('resource'))


class DeleteAvailabilityChange(Command, AvailabilityCommandHelpers):
    def availability(self):
        return self.input_data['availability']

    def _check_if_valid(self):
        if not self.can_administer_resource():
            return self.unauthorized()

        if self.availability().start_date < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self.has_errors()

    def _execute_on_valid(self):
        self.availability().delete()
        self.result_data = {
            'deleted': {'availability': [self.availability().pk]}
        }

    def resource(self):
        return self.availability().resource
