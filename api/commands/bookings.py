from api.command import *
from core.models import Resource


class RequestBooking(FormCommand):
    class Form(forms.Form):
        arrive = forms.DateField()
        depart = forms.DateField()
        resource = forms.ModelChoiceField(queryset=Resource.objects.all())

        def clean(self):
            cleaned_data = super(RequestBooking.Form, self).clean()

            arrive = cleaned_data.get('arrive')
            depart = cleaned_data.get('depart')
            resource = cleaned_data.get('resource')

            if depart and arrive:
                if depart < arrive:
                    self.add_error('depart', "Must be after arrival date")

                if resource:
                    location = resource.location
                    if location:
                        if (depart - arrive).days > location.max_booking_days:
                            self.add_error('depart', [
                                'Sorry! We only accept booking requests greater than %s in special circumstances. Please limit your request to %s or shorter, and add a comment if you would like to be consdered for a longer stay.' % (location.max_booking_days, location.max_booking_days)
                            ])
                    else:
                        self.add_error('resource', "Must have a location")

            # try:
            #     cleaned_data['resource'] = Resource.objects.get(pk=cleaned_data.get('resource_id'))
            # except Resource.DoesNotExist:
            #     self.add_error('resource', "not found")

            return cleaned_data

    def _execute_on_valid(self):
        pass
