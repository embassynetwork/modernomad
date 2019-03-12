# -*- coding: utf-8 -*-
import importlib
from django.contrib.auth.models import User
from django.test import TestCase

# Python can't import modules starting with a number
fix_usernames = importlib.import_module('modernomad.core.migrations.0071_fix_usernames').fix_usernames


class FixUsernamesTest(TestCase):
    def test_fix_usernames(self):
        user1 = User.objects.create(username="1", first_name="Hm", last_name="😎")
        user2 = User.objects.create(username="2", first_name="🙀")
        user3 = User.objects.create(username="3", first_name="😂")
        user4 = User.objects.create(username='4', first_name="Joe", last_name="Uppercase")
        user5 = User.objects.create(username='5', first_name="Joe", last_name="uppercase")

        fix_usernames(User)

        self.assertEqual(User.objects.get(pk=user1.pk).username, 'hm')
        self.assertEqual(User.objects.get(pk=user2.pk).username, 'unnamed')
        self.assertEqual(User.objects.get(pk=user3.pk).username, 'unnamed-2')
        self.assertEqual(User.objects.get(pk=user4.pk).username, 'joe-uppercase')
        self.assertEqual(User.objects.get(pk=user5.pk).username, 'joe-uppercase-2')
