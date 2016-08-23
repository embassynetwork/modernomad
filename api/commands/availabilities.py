from api.command import *
from datetime import datetime


class AddAvailabilityChange(ModelCreationBaseCommand):
    def _model_class(self):
        return AvailabilitySerializer

    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False

        if self.validated_data('start_date') < datetime.now(self._tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self._has_errors()

    def _execute_on_valid(self):
        if self._would_not_change_quantity():
            self.add_warning('quantity', u'This is not a change from the previous availability')
            return

        self._save_deserialized_model()

    def _tz(self):
        return self.validated_data('resource').tz()

    def _would_not_change_quantity(self):
        return self._previous_quantity() == self.validated_data('quantity')

    def _previous_quantity(self):
        return Availability.objects.quantity_on(self.validated_data('start_date'), self.validated_data('resource'))


class DeleteAvailabilityChange(Command):
    def availability(self):
        return self.input_data['availability']

    def _check_if_valid(self):
        if self.availability().start_date < datetime.now(self._tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self._has_errors()

    def _execute_on_valid(self):
        self.availability().delete()
        self.result_data = {
            'deleted': {'availability': [self.availability().pk]}
        }

    def _tz(self):
        return self.availability().resource.tz()
