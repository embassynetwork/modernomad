from modernomad.core.serializers import *
from django import forms


class CommandResult:
    def __init__(self, data=None, errors={}, warnings={}):
        self.data = data
        self.errors = errors
        self.warnings = warnings

    def serialize(self):
        result = {}
        if self.data:
            result['data'] = self.data
        if self.errors:
            result['errors'] = self.errors
        if self.warnings:
            result['warnings'] = self.warnings

        return result


class CommandSuccess(CommandResult):
    def http_status(self):
        return 200


class CommandFailed(CommandResult):
    def http_status(self):
        return 400


class CommandUnauthorized(CommandResult):
    def http_status(self):
        return 403


class Command:
    def __init__(self, issuing_user, **kwargs):
        self.executed = False
        self.valid = None
        self.result_object = None
        self.issuing_user = issuing_user
        self.input_data = kwargs
        self.result_data = None
        self.errors = {}
        self.warnings = {}
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

    def add_warning(self, field, message):
        self.warnings.setdefault(field, []).append(message)

    def unauthorized(self):
        self.add_error('auth', 'does not have permission to do this')
        return False

    def is_authorized(self):
        bool(self.errors.get('auth', []))

    def has_errors(self):
        return bool(self.errors)

    def _setup(self):
        pass

    def _get_result(self):
        assert self.executed, "You must execute this command before asking for the result"

        if self.is_valid():
            return self._get_success_result()
        elif self.is_authorized():
            return self._get_unauthorized_result()
        else:
            return self._get_failure_result()

    def _get_success_result(self):
        return CommandSuccess(data=self.result_data, warnings=self.warnings)

    def _get_unauthorized_result(self):
        return CommandUnauthorized(errors=self.errors)

    def _get_failure_result(self):
        return CommandFailed(errors=self.errors, warnings=self.warnings)

    def _check_if_valid(self):
        return True

    def _execute_on_valid(self):
        raise Exception("override _execute_on_valid to make your command work")

class FormCommand(Command):
    def _setup(self):
        form_class = self._form_class()
        self.form = form_class(self.input_data)

    def _form_class(self):
        return self.Form

    def _check_if_valid(self):
        return self._check_if_form_valid()

    def _check_if_form_valid(self):
        result = self.form.is_valid()
        self._append_form_errors()
        self.cleaned_data = self.form.cleaned_data
        return result

    def _append_form_errors(self):
        if self.form.errors:
            for field_name, messages in self.form.errors.items():
                for message in messages:
                    self.add_error(field_name, message)
