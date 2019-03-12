# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from modernomad.core.forms import UserProfileForm, create_username


class UserProfileFormTest(TestCase):
    def test_create_username(self):
        self.assertEqual(create_username('Joe', '⛄️ Bloggs'), 'joe-bloggs')
        self.assertEqual(create_username('Joe', 'Bloggs Smith'), 'joe-bloggs-smith')
        self.assertEqual(create_username('Joe', 'Smith', suffix="1"), 'joe-smith-1')
        self.assertEqual(create_username('Joe', 'Blooooooooooooooooooooooooooooooooooooooooooooooooggs'), 'joe-blooooooooooooooooooo')
        self.assertEqual(create_username('Joe', 'Blooooooooooooooooooooooooooooooooooooooooooooooooggs', suffix="2"), 'joe-blooooooooooooooooooo-2')

    def test_users_are_given_unique_usernames(self):
        # If joe-bloggs doesn't exist, user is given normal username
        form = UserProfileForm({
            'first_name': 'Joe',
            'last_name': 'Bloggs',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data['username'], 'joe-bloggs')

        user = User(username='joe-bloggs',
                    first_name='Joe', last_name='Bloggs')
        user.set_password('password')
        user.save()

        # If joe-bloggs does exist, suffix is added
        form = UserProfileForm({
            'first_name': 'Joe',
            'last_name': 'Bloggs',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data['username'], 'joe-bloggs-2')
