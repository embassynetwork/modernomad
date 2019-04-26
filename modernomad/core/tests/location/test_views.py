from django.shortcuts import reverse
from django.test import TestCase
from modernomad.core.factory_apps.location import LocationFactory, ResourceFactory
from modernomad.core.factory_apps.user import UserFactory


class LocationDetailTest(TestCase):

    def setUp(self):
        user = UserFactory(username="embassysfadmin", first_name="SF", last_name="Admin")
        self.location = LocationFactory(slug="embassysf", name="Embassy SF", house_admins=[user])
        ResourceFactory(location=self.location, name="Batcave")
        ResourceFactory(location=self.location, name="Ada Lovelace")
        self.url = reverse('location_detail', kwargs={'slug': self.location.slug})

    def test_location_visible(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
