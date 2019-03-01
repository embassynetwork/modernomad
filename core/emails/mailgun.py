from django.http import HttpResponse
from django.conf import settings
from sentry_sdk import capture_exception, capture_message
import logging
import requests
logger = logging.getLogger(__name__)

def mailgun_send(mailgun_data, files_dict=None):
    logger.debug("Mailgun send: %s" % mailgun_data)
    logger.debug("Mailgun files: %s" % files_dict)

    if not settings.MAILGUN_API_KEY:
        capture_message("Mailgun API key is not defined.")
        return HttpResponse(status=500)

    if not settings.MAILGUN_CAUTION_SEND_REAL_MAIL:
        # We will see this message in the mailgun logs but nothing will
        # actually be delivered. This gets added at the end so it can't be
        # overwritten by other functions.
        mailgun_data["o:testmode"] = "yes"
        logger.debug("mailgun_send: o:testmode=%s" % mailgun_data["o:testmode"])

    try:
        resp = requests.post("https://api.mailgun.net/v2/%s/messages" % settings.LIST_DOMAIN,
            auth=("api", settings.MAILGUN_API_KEY),
            data=mailgun_data,
            files=files_dict
        )

        if resp.status_code != 200:
            capture_message('Mailgun POST returned %d' % resp.status_code)
        return HttpResponse(status=resp.status_code)

    except requests.ConnectionError as e:
        logger.error('Connection error. Email "%s" aborted.' % mailgun_data['subject'])
        capture_exception(e)
        return HttpResponse(status=500)


