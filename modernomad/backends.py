from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
import logging

logger = logging.getLogger(__name__)

# Imported from Nadine
# https://github.com/nadineproject/nadine


class EmailOrUsernameModelBackend(object):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            email_username = username.lower()
            kwargs = {'email': email_username, 'is_active': True}
        else:
            kwargs = {'username': username, 'is_active': True}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
