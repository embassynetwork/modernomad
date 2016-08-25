from django.test import TestCase
from core.factories import *
from api.commands.availabilities import *
from core.models import *


class AddAvailabilityChangeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.resource.location.house_admins.add(self.user)

    def test_that_command_with_valid_data_creates_an_availability(self):
        command = AddAvailabilityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=2)

        if not command.execute():
            print command.result()
            self.assertTrue(False)

        availability = Availability.objects.filter(resource=self.resource).last()
        self.assertTrue(availability)
        self.assertEqual(availability.quantity, 2)
        self.assertEqual(availability.start_date, datetime.date(4016, 1, 13))

        expected_data = {'quantity': 2, 'resource': self.resource.pk, 'id': availability.pk, 'start_date': '4016-01-13'}
        self.assertEqual(command.result().serialize(), {'data': expected_data})

    def test_that_command_from_non_house_admin_fails(self):
        non_admin = UserFactory(username="samwise")
        command = AddAvailabilityChange(non_admin, start_date="4016-01-13", resource=self.resource.pk, quantity=2)
        self.assertFalse(command.execute())

    def test_that_command_with_missing_data_fails(self):
        command = AddAvailabilityChange(self.user, resource=self.resource.pk, quantity=2)

        self.assertFalse(command.execute())

        expected_data = {'errors': {'start_date': [u'This field is required.']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_a_date_in_the_past_fails(self):
        command = AddAvailabilityChange(self.user, start_date="1016-01-13", resource=self.resource.pk, quantity=2)

        self.assertFalse(command.execute())

        expected_data = {'errors': {
            'start_date': [u'The start date must not be in the past']
        }}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_changing_availability_to_the_same_quantity_has_no_effect(self):
        command1 = AddAvailabilityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=2)
        command1.execute()

        command2 = AddAvailabilityChange(self.user, start_date="4016-01-15", resource=self.resource.pk, quantity=2)
        self.assertTrue(command2.execute())
        self.assertEqual(Availability.objects.count(), 1)

        expected_data = {'warnings': {'quantity': [u'This is not a change from the previous availability']}}
        self.assertEqual(command2.result().serialize(), expected_data)

    def test_availability_cant_have_same_date_as_another_for_same_resource(self):
        command1 = AddAvailabilityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=2)
        command1.execute()

        command2 = AddAvailabilityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=2)
        self.assertFalse(command2.execute())
        self.assertEqual(Availability.objects.count(), 1)

        expected_data = {'errors': {u'non_field_errors': [u'The fields start_date, resource must make a unique set.']}}
        self.assertEqual(command2.result().serialize(), expected_data)


class DeleteAvailabilityChangeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.resource.location.house_admins.add(self.user)

    def test_that_command_from_non_house_admin_fails(self):
        availability = Availability.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        non_admin = UserFactory(username="samwise")
        command = DeleteAvailabilityChange(non_admin, availability=availability)
        self.assertFalse(command.execute())

    def test_can_delete_availability_in_the_future(self):
        availability = Availability.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)

        command = DeleteAvailabilityChange(self.user, availability=availability)
        self.assertTrue(command.execute())
        self.assertEqual(Availability.objects.count(), 0)
        expected_data = {'data': {'deleted': {'availability': [availability.pk]}}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_cant_delete_availability_in_the_past(self):
        availability = Availability.objects.create(start_date=datetime.date(1016, 1, 13), resource=self.resource, quantity=2)

        command = DeleteAvailabilityChange(self.user, availability=availability)
        self.assertFalse(command.execute())
        self.assertEqual(Availability.objects.count(), 1)
        expected_data = {'errors': {'start_date': [u'The start date must not be in the past']}}
        self.assertEqual(command.result().serialize(), expected_data)
