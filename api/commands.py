from command import *
from datetime import datetime
from pytz import timezone


class AddAvailabilityChange(ModelCreationBaseCommand):
    def _model_class(self):
        return AvailabilitySerializer

    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False

        if self.validated_data('start_date') < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self._has_errors()

    def tz(self):
        return self.validated_data('resource').tz()
