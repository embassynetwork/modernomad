from api.command import *
from datetime import datetime
from core.models import Resource
from django.core.exceptions import ValidationError


def user_can_administer_a_resource(user, resource):
    return (
        user and
        resource and
        resource.location and
        (
            user in resource.backers() 
            or 
            user in resource.location.house_admins.all()
        )
    )


class CapacityCommandHelpers:
    def tz(self):
        return self.resource().tz()

    def current_date_for_tz(self):
        return datetime.now(self.tz()).date()

    def can_administer_resource(self):
        return user_can_administer_a_resource(self.issuing_user, self.resource())

    def _validate_not_in_past(self):
        if self.start_date() < self.current_date_for_tz():
            self.add_error('start_date', u'The start date must not be in the past')

    def _resource_capacities(self, order='start_date'):
        return CapacityChange.objects.filter(resource=self.resource()).order_by(order)

    def _next_capacity(self):
        return self._resource_capacities('start_date').filter(start_date__gt=self.start_date()).first()

    def _previous_capacity(self):
        return self._resource_capacities('-start_date').filter(start_date__lt=self.start_date()).first()

    def _would_not_change_previous_quantity(self):
        return self._previous_capacity() and (self._previous_capacity().quantity == self.validated_data('quantity') and self._previous_capacity().accept_drft == self.validated_data('accept_drft'))

    def _delete_next_quantity(self):
        self._next_capacity().delete()
        # update self.result_data in Command() class

    def _same_as_next_quantity(self):
        print 'same_as_next_quantity'
        print self._next_capacity()
        if self._next_capacity():
            print self._next_capacity().quantity
            print self._next_capacity().accept_drft
        print self.validated_data('quantity')
        print self.validated_data('accept_drft')

        if (self._next_capacity() and 
            ( self._next_capacity().quantity == self.validated_data('quantity') )
            and 
            ( self._next_capacity().accept_drft == self.validated_data('accept_drft') )
        ):
            return True
        return False

    def _check_next_and_previous(self):
        # NB: I was hoping to be able to use this in UpdateCapacityChange as
        # well as AddCapacityChange, but the former doesn't use a
        # self.validated_data() method, so aborting but leaving here
        # aspiratonally. 
        if self._would_not_change_previous_quantity():
            self.add_warning('Oops', u'This is not a change from the previous capacity')
            return
        if self._same_as_next_quantity():
            self.add_warning('FYI', u'The capacity change was combined with the one following it, which was the same.')
            self._delete_next_quantity()

class SerializedCapacityCommand(SerializedModelCommand):
    def _model_class(self):
        return CapacityChangeSerializer

    def resource(self):
        return self.validated_data('resource')

    def accept_drft(self):
        return self.validated_data('accept_drft')

    def start_date(self):
        return self.validated_data('start_date')


class UpdateOrAddCapacityChange(DecoratorCommand, CapacityCommandHelpers):
    def _determine_inner(self):
        existing = self._fetch_existing_capacity_for_date(self.start_date())
        if existing:
            self.inner_command = UpdateCapacityChange(self.issuing_user, capacity=existing, quantity=self.input_data.get('quantity'), accept_drft=self.input_data.get('accept_drft'))
        else:
            self.inner_command = AddCapacityChange(self.issuing_user, **self.input_data)

    def resource(self):
        return Resource.objects.get(pk=self.input_data['resource'])

    def start_date(self):
        date_string = self.input_data.get('start_date')
        if date_string:
            return datetime.strptime(date_string, "%Y-%m-%d").date()

    def _fetch_existing_capacity_for_date(self, start_date):
        return self._resource_capacities().filter(start_date=start_date).first()


class UpdateCapacityChange(ModelCommand, CapacityCommandHelpers):
    def _check_if_valid(self):
        if not self.can_administer_resource():
            return self.unauthorized()

        self.model().quantity = self.input_data['quantity']
        self.model().accept_drft = self.input_data['accept_drft']

        self._validate_not_in_past()
        self._is_model_valid()

        return not self.has_errors()

    def model(self):
        return self.input_data['capacity']

    def resource(self):
        return self.model().resource

    def start_date(self):
        return self.model().start_date

    def _serialize_model(self):
        return CapacityChangeSerializer(self.model()).data

    def _execute_on_valid(self):
        #self._check_next_and_previous()
        super(UpdateCapacityChange, self)._execute_on_valid()

class AddCapacityChange(SerializedCapacityCommand, CapacityCommandHelpers):
    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False

        if not self.can_administer_resource():
            return self.unauthorized()

        self._validate_not_in_past()

        return not self.has_errors()

    def _execute_on_valid(self):
        self._check_next_and_previous()
        self._save_deserialized_model()


class DeleteCapacityChange(Command, CapacityCommandHelpers):
    def capacity(self):
        return self.input_data['capacity']

    def start_date(self):
        return self.capacity().start_date

    def resource(self):
        return self.capacity().resource

    def _check_if_valid(self):
        if not self.can_administer_resource():
            return self.unauthorized()

        self._validate_not_in_past()

        return not self.has_errors()

    def _execute_on_valid(self):
        to_delete = self._to_delete()
        keys = [record.pk for record in to_delete]
        for record in to_delete:
            record.delete()

        self.result_data = {'deleted': {'capacities': keys}}

    def _to_delete(self):
        result = [self.capacity()]
        next_avail = self._next_capacity()

        if next_avail:
            previous_avail = self._previous_capacity()
            if (previous_avail and previous_avail.quantity == next_avail.quantity):
                result.append(next_avail)
        return result
