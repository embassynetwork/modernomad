from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.core.exceptions import MultipleObjectsReturned

from io import StringIO
import requests
import logging

logger = logging.getLogger(__name__)

class MailgunAPIError(Exception):
    pass

# Imported from django-mailgun
# https://github.com/bradwhittington/django-mailgun/
class MailgunBackend(BaseEmailBackend):
    """A Django Email backend that uses mailgun.
    """

    def __init__(self, fail_silently=False, *args, **kwargs):
        access_key, server_name = (kwargs.pop('access_key', None),
                                   kwargs.pop('server_name', None))

        super(MailgunBackend, self).__init__(
                        fail_silently=fail_silently,
                        *args, **kwargs)

        try:
            self._access_key = access_key or getattr(settings, 'MAILGUN_API_KEY')
            self._server_name = server_name or getattr(settings, 'LIST_DOMAIN')
        except AttributeError:
            if fail_silently:
                self._access_key, self._server_name = None, None
            else:
                raise

        self._api_url = "https://api.mailgun.net/v2/%s/" % self._server_name
        logger.debug("Mailgun URL: %s" % self._api_url)

    def open(self):
        """Stub for open connection, all sends are done over HTTP POSTs
        """
        pass

    def close(self):
        """Close any open HTTP connections to the API server.
        """
        pass

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]

        try:
            r = requests.post(self._api_url + "messages.mime",
                     auth=("api", self._access_key),
                     data={
                            "to": ", ".join(recipients),
                            "from": from_email,
                         },
                     files={
                            "message": StringIO(email_message.message().as_string()),
                         }
                     )
        except:
            if not self.fail_silently:
                raise
            return False

        logger.debug("Mailgun response: %s" % r.text)

        if r.status_code != 200:
            if not self.fail_silently:
                raise MailgunAPIError(r)
            return False

        return True

    def send_messages(self, email_messages):
        """Sends one or more EmailMessage objects and returns the number of
        email messages sent.
        """
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1

        return num_sent

# Imported from Nadine
# https://github.com/nadineproject/nadine
class EmailOrUsernameModelBackend(object):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            email_username = username.lower()
            kwargs = {'email': email_username, 'is_active':True}
        else:
            kwargs = {'username': username, 'is_active':True}
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
