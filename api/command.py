from core.serializers import *


class CommandResult:
    def __init__(self, data=None, errors=[]):
        self.data = data
        self.errors = errors


class CommandSuccess(CommandResult):
    def serialize(self):
        return self.data


class CommandFailed(CommandResult):
    def serialize(self):
        return {'errors': self.errors}


class Command:
    def __init__(self, issuing_user, **kwargs):
        self.executed = False
        self.valid = None
        self.result_object = None
        self.issuing_user = issuing_user
        self.data = kwargs
        self.errors = {}
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

    def add_error(self, field, message):
        self.errors.setdefault(field, []).append(message)

    def _has_errors(self):
        return bool(self.errors)

    def _setup(self):
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
        return CommandFailed(errors=self.errors)

    def _check_if_valid(self):
        return True

    def _execute_on_valid(self):
        raise Exception("override _execute_on_valid to make your command work")


class ModelCreationBaseCommand(Command):
    def validated_data(self, key):
        return self.deserialized_model.validated_data[key]

    def _setup(self):
        model_class = self._model_class()
        self.deserialized_model = model_class(data=self.data)

    def _check_if_valid(self):
        return _check_if_model_valid()

    def _check_if_model_valid(self):
        result = self.deserialized_model.is_valid()
        self._append_model_errors()
        return result

    def _execute_on_valid(self):
        return self.deserialized_model.save()

    def _get_success_result(self):
        return CommandSuccess(data=self.deserialized_model.data)

    def _get_failure_result(self):
        return CommandFailed(errors=self.errors)

    def _append_model_errors(self):
        if self.deserialized_model.errors:
            for field_name, messages in self.deserialized_model.errors.iteritems():
                for message in messages:
                    self.add_error(field_name, message)
