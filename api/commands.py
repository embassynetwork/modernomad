from core.serializers import *
import datetime


class CommandResult:
    def __init__(self, data=None, errors=[]):
        self.data = data
        self.errors = errors


class CommandSuccess(CommandResult):
    def serialize(self):
        return self.data


class CommandFailed(CommandResult):
    def serialize(self):
        return self.errors


class Command:
    def __init__(self, issuing_user, **kwargs):
        self.executed = False
        self.valid = None
        self.result_object = None
        self.issuing_user = issuing_user
        self.data = kwargs
        self._setup()

    def is_valid(self):
        if self.valid is None:
            self.valid = self._check_if_valid()

        return self.valid

    def result(self):
        if self.result_object is None:
            self.result_object = self._get_result()

        return self.result_object

    def execute(self):
        if self.is_valid():
            self.executed = True
            self._execute_on_valid()
            return True
        else:
            self.executed = True
            return False

    def _setup():
        pass

    def _get_result(self):
        assert self.executed, "You must execute this command before asking for the result"

        if self.is_valid():
            return self._get_success_result()
        else:
            return self._get_failure_result()

    def _get_success_result(self):
        return CommandSuccess()

    def _get_failure_result(self):
        return CommandFailed()

    def _check_if_valid(self):
        return True

    def _execute_on_valid(self):
        raise Exception("override _execute_on_valid to make your command work")


class ModelCreationBaseCommand(Command):
    def _setup(self):
        model_class = self._model_class()
        self.deserialized_model = model_class(data=self.data)

    def _check_if_valid(self):
        return _check_if_model_valid()

    def _check_if_model_valid(self):
        return self.deserialized_model.is_valid()

    def _execute_on_valid(self):
        return self.deserialized_model.save()

    def _get_success_result(self):
        return CommandSuccess(data=self.deserialized_model.data)

    def _get_failure_result(self):
        return CommandFailed(errors=self.deserialized_model.errors)


class AddAvailabilityChange(ModelCreationBaseCommand):
    def _model_class(self):
        return AvailabilitySerializer

    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False
        if self.deserialized_model.validated_data['start_date'] < datetime.date.today():
            return False
