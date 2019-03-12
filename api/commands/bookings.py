from api.command import *
from modernomad.core.models import Resource, Booking, Use
from django.db import transaction


class RequestBooking(FormCommand):
    class Form(forms.Form):
        arrive = forms.DateField()
        depart = forms.DateField()
        resource = forms.ModelChoiceField(queryset=Resource.objects.all())
        purpose = forms.CharField(required=False)
        arrival_time = forms.CharField(required=False)
        comments = forms.CharField(required=False)

        def clean(self):
            cleaned_data = super(RequestBooking.Form, self).clean()

            arrive = cleaned_data.get('arrive')
            depart = cleaned_data.get('depart')
            resource = cleaned_data.get('resource')

            if depart and arrive and resource:
                if depart < arrive:
                    self.add_error('depart', "Must be after arrival date")

                location = resource.location
                if location:
                    if (depart - arrive).days > location.max_booking_days:
                        self.add_error('depart', [
                            'Sorry! We only accept booking requests greater than %s in special circumstances. Please limit your request to %s or shorter, and add a comment if you would like to be consdered for a longer stay.' % (location.max_booking_days, location.max_booking_days)
                        ])
                else:
                    self.add_error('resource', "Must have a location")

            return cleaned_data

    def _execute_on_valid(self):
        data = self.cleaned_data

        with transaction.atomic():
            use = Use(
                arrive=data['arrive'], depart=data['depart'],
                user=self.issuing_user,
                resource=data['resource'], location=data['resource'].location
            )
            use.save()

            booking = Booking(
                use=use, comments=data.get('comments'),
                rate=data['resource'].default_rate
            )
            booking.save()

            self.result_data = {
                "booking": booking,
                "use": use
            }
