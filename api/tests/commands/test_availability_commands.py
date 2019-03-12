from django.test import TestCase
import unittest

from modernomad.core.factories import *
from api.commands.capacities import *
from modernomad.core.models import *

@unittest.skip("needs fixing after refactoring in ac1c446e4758b2552e5d1bc08c9f832faa31a3a0")
class AddCapacityChangeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.resource.location.house_admins.add(self.user)

    def test_that_command_with_valid_data_creates_an_capacity(self):
        command = UpdateOrAddCapacityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=2)

        if not command.execute():
            self.assertTrue(False)

        capacity = CapacityChange.objects.filter(resource=self.resource).last()
        self.assertTrue(capacity)
        self.assertEqual(capacity.quantity, 2)
        self.assertEqual(capacity.start_date, datetime.date(4016, 1, 13))

        expected_data = {'quantity': 2, 'resource': self.resource.pk, 'id': capacity.pk, 'start_date': '4016-01-13'}
        self.assertEqual(command.result().serialize(), {'data': expected_data})

    def test_that_command_from_non_house_admin_fails(self):
        non_admin = UserFactory(username="samwise")
        command = UpdateOrAddCapacityChange(non_admin, start_date="4016-01-13", resource=self.resource.pk, quantity=2)
        self.assertFalse(command.execute())

    def test_that_command_with_missing_data_fails(self):
        command = UpdateOrAddCapacityChange(self.user, resource=self.resource.pk, quantity=2)

        self.assertFalse(command.execute())

        expected_data = {'errors': {'start_date': [u'This field is required.']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_a_date_in_the_past_fails(self):
        command = UpdateOrAddCapacityChange(self.user, start_date="1016-01-13", resource=self.resource.pk, quantity=2)

        self.assertFalse(command.execute())

        expected_data = {'errors': {
            'start_date': [u'The start date must not be in the past']
        }}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_changing_capacity_to_the_same_quantity_has_no_effect(self):
        capacity = CapacityChange.objects.create(start_date="4016-01-13", resource=self.resource, quantity=2)

        command = UpdateOrAddCapacityChange(self.user, start_date="4016-01-15", resource=self.resource.pk, quantity=2)
        self.assertTrue(command.execute())
        self.assertEqual(CapacityChange.objects.count(), 1)

        expected_data = {'warnings': {'quantity': [u'This is not a change from the previous capacity']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_setting_capacity_to_another_quantity_updates_a_record_on_that_date(self):
        capacity = CapacityChange.objects.create(start_date="4016-01-13", resource=self.resource, quantity=2)

        command = UpdateOrAddCapacityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=3)
        self.assertTrue(command.execute())
        self.assertEqual(CapacityChange.objects.count(), 1)

        expected_data = {'quantity': 3, 'resource': self.resource.pk, 'id': capacity.pk, 'start_date': '4016-01-13'}
        self.assertEqual(command.result().serialize(), {'data': expected_data})

    def test_cannot_udpate_capacity_in_the_past(self):
        capacity = CapacityChange.objects.create(start_date="1016-01-13", resource=self.resource, quantity=2)

        command = UpdateOrAddCapacityChange(self.user, start_date="1016-01-13", resource=self.resource.pk, quantity=3)
        self.assertFalse(command.execute())
        self.assertEqual(CapacityChange.objects.count(), 1)

        expected_data = {'errors': {'start_date': [u'The start date must not be in the past']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_update_command_from_non_house_admin_fails(self):
        capacity = CapacityChange.objects.create(start_date="4016-01-13", resource=self.resource, quantity=2)

        non_admin = UserFactory(username="samwise")
        command = UpdateOrAddCapacityChange(non_admin, start_date="4016-01-13", resource=self.resource.pk, quantity=3)
        self.assertFalse(command.execute())


class DeleteCapacityChangeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.resource.location.house_admins.add(self.user)

    def expect_deleted_capacities(self, expected_ids, remaining=0):
        self.assertTrue(self.command.execute())
        self.assertEqual(CapacityChange.objects.count(), remaining)
        expected_data = {'data': {'deleted': {'capacities': expected_ids}}}
        self.assertEqual(self.command.result().serialize(), expected_data)

    def test_that_command_from_non_house_admin_fails(self):
        capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        non_admin = UserFactory(username="samwise")
        self.command = DeleteCapacityChange(non_admin, capacity=capacity)
        self.assertFalse(self.command.execute())

    def test_cant_delete_capacity_in_the_past(self):
        capacity = CapacityChange.objects.create(start_date=datetime.date(1016, 1, 13), resource=self.resource, quantity=2)

        command = DeleteCapacityChange(self.user, capacity=capacity)
        self.assertFalse(command.execute())
        self.assertEqual(CapacityChange.objects.count(), 1)
        expected_data = {'errors': {'start_date': [u'The start date must not be in the past']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_can_delete_capacity_in_the_future(self):
        capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        self.command = DeleteCapacityChange(self.user, capacity=capacity)
        self.expect_deleted_capacities([capacity.pk])

    def test_deleting_capacity_also_deletes_next_one_if_it_is_the_same_as_previous(self):
        previous_capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 12), resource=self.resource, quantity=3)
        capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        next_capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 14), resource=self.resource, quantity=3)
        self.command = DeleteCapacityChange(self.user, capacity=capacity)
        self.expect_deleted_capacities([capacity.pk, next_capacity.pk], remaining=1)

    def test_deleting_capacity_doesnt_deletes_next_one_if_it_different_to_previous(self):
        previous_capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 12), resource=self.resource, quantity=4)
        capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        next_capacity = CapacityChange.objects.create(start_date=datetime.date(4016, 1, 14), resource=self.resource, quantity=3)
        self.command = DeleteCapacityChange(self.user, capacity=capacity)
        self.expect_deleted_capacities([capacity.pk], remaining=2)
