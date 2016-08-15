from command import *
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
            return True

        return self.deserialized_model.save()

    def _tz(self):
        return self.validated_data('resource').tz()

    def _would_not_change_quantity(self):
        return self._previous_quantity() == self.validated_data('quantity')

    def _previous_quantity(self):
        return Availability.quantity_on(self.validated_data('start_date'))
