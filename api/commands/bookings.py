from api.command import *
from django import forms


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
        return result

    def _append_form_errors(self):
        if self.form.errors:
            for field_name, messages in self.form.errors.iteritems():
                for message in messages:
                    self.add_error(field_name, message)



class RequestBooking(FormCommand):
    class Form(forms.Form):
        arrive = forms.DateField()
        depart = forms.DateField()

    def _execute_on_valid(self):
        pass
