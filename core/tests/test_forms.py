# -*- coding: utf-8 -*-
from django.test import TestCase
from core.forms import UserProfileForm


class UserProfileFormTest(TestCase):
    def test_create_username(self):
        form = UserProfileForm({
            'first_name': 'Joe',
            'last_name': '⛄️ Bloggs',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data['username'], 'joe-bloggs')
