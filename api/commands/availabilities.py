from api.command import *
from datetime import datetime


def user_can_administer_a_resource(user, resource):
    return (
        user and
        resource and
        resource.location and
        user in resource.location.house_admins.all()
    )


class AvailabilityCommandHelpers:
    def tz(self):
        return self.resource().tz()

    def can_administer_resource(self):
        return user_can_administer_a_resource(self.issuing_user, self.resource())


class AddAvailabilityChange(ModelCreationBaseCommand, AvailabilityCommandHelpers):
    def _model_class(self):
        return AvailabilitySerializer

    def _check_if_valid(self):
        if not self._check_if_model_valid():
            return False

        if not self.can_administer_resource():
            return self.unauthorized()

        if self.validated_data('start_date') < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self.has_errors()

    def _execute_on_valid(self):
        if self._would_not_change_previous_quantity():
            self.add_warning('quantity', u'This is not a change from the previous availability')
            return
        if self._same_as_next_quantity():
            self.add_warning('quantity', u'The availability change was combined with the one following it, which was the same.')
            self._delete_next_quantity()

        self._save_deserialized_model()

    def resource(self):
        return self.validated_data('resource')

    def _would_not_change_previous_quantity(self):
        return self._previous_quantity() == self.validated_data('quantity')

    def _delete_next_quantity(self):
        self._next_availability().delete()

    def _same_as_next_quantity(self):
        return self._next_quantity() == self.validated_data('quantity')

    def _next_availability(self):
        next_avail = Availability.objects.filter(start_date__gt=self.validated_data('start_date'), resource=self.validated_data('resource')).order_by('start_date').first()
        print next_avail.start_date, next_avail.quantity
        return next_avail

    def _next_quantity(self):
        return self._next_availability().quantity

    def _previous_quantity(self):
        return Availability.objects.quantity_on(self.validated_data('start_date'), self.validated_data('resource'))


class DeleteAvailabilityChange(Command, AvailabilityCommandHelpers):
    def availability(self):
        return self.input_data['availability']

    def _check_if_valid(self):
        if not self.can_administer_resource():
            return self.unauthorized()

        if self.availability().start_date < datetime.now(self.tz()).date():
            self.add_error('start_date', u'The start date must not be in the past')

        return not self.has_errors()

    def _get_prev_and_next_indexes(self, avail, all_avails):
        # keep the availabilities in increasing-date-order here, so that 'next'
        # is intuitive (future date)
        idx = all_avails.index(avail)

        if len(all_avails) > idx+1: 
            next = idx+1 
        else:
            next = None

        if idx != 0:
            prev = idx-1 
        else: 
            prev = None

        return (prev, next)

    def adjust_adjacent(self):
        print 'in adjust adjacent'
        this_avail = self.input_data['availability']
        all_avails = list(Availability.objects.filter(resource=this_avail.resource).order_by('start_date'))
        prev, next = self._get_prev_and_next_indexes(this_avail, all_avails)
        if prev is None or next is None:
            print 'no adjustments needed'
            return None

        print 'prev and next availabilities'
        print all_avails[prev].id, all_avails[prev].start_date, all_avails[prev].quantity  
        print all_avails[next].id, all_avails[next].start_date, all_avails[next].quantity  

        delete_idxs = []
        if all_avails[next].quantity == all_avails[prev].quantity:
            print 'adjusting'
            to_delete = all_avails[next]
            deleted_pk = to_delete.pk
            to_delete.delete()
            print 'deleted_pk'
            print deleted_pk
            return deleted_pk
        else:
            print 'quantities were different, moving on'

    def _execute_on_valid(self):
        deleted_id = self.adjust_adjacent()
        deleted_list = [self.availability().pk]
        self.availability().delete()
        if deleted_id:
            deleted_list.append(deleted_id)
        self.result_data = {
            'deleted': {'availabilities': deleted_list}
        }

    def resource(self):
        return self.availability().resource
