from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.conf import settings
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from gather.models import Event, EventAdminGroup, EventSeries, EventNotifications
from django.contrib.auth.models import User
import requests
import logging
import json

logger = logging.getLogger(__name__)

from modernomad.core.emails.mailgun import mailgun_send

def new_event_notification(event, location):
    # notify the event admins that a new event has been proposed
    admin_group = event.admin
    recipients = [admin.email for admin in admin_group.users.all()]
    event_short_title = event.title[0:50]
    if len(event.title) > 50:
        event_short_title = event_short_title + "..."
    subject = '[' + location.email_subject_prefix + ']' + " A new event has been created: %s" % event_short_title
    from_address = location.from_email()
    plaintext = get_template('emails/new_event_notify.txt')
    c = {
        'event': event,
        'location': location,
        'domain': Site.objects.get_current().domain,
    }
    body_plain = plaintext.render(c)
    mailgun_data = {
        "from": from_address,
        "to": recipients,
        "subject": subject,
        "text": body_plain,
    }
    return mailgun_send(mailgun_data)

def event_approved_notification(event, location):
    ''' send an email to organizers letting them know their event has been approved.'''
    logger.debug("event_approved_notification")
    recipients = [organizer.email for organizer in event.organizers.all()]
    subject = '[' + location.email_subject_prefix + ']' + " Your event is ready to be published"
    from_address = location.from_email()
    plaintext = get_template('emails/event_approved_notify.txt')
    c = {
        'event': event,
        'domain': Site.objects.get_current().domain,
        'location': location,
    }
    body_plain = plaintext.render(c)
    mailgun_data = {
        "from": from_address,
        "to": recipients,
        "subject": subject,
        "text": body_plain,
    }
    return mailgun_send(mailgun_data)

def event_published_notification(event, location):
    ''' notify event organizers and subscribed members that their event is live'''
    logger.debug("event_published_notification")

    event_short_title = event.title[0:50]
    if len(event.title) > 50:
        event_short_title = event_short_title + "..."

    # first notify organizers
    recipients = [organizer.email for organizer in event.organizers.all()]
    subject = '[' + location.email_subject_prefix + ']' + " Your event is now live: %s" % event_short_title
    from_address = location.from_email()
    plaintext = get_template('emails/event_published_notify.txt')
    c = {
        'event': event,
        'domain' : Site.objects.get_current().domain,
        'location': location,
    }
    body_plain = plaintext.render(c)
    mailgun_data = {
        "from": from_address,
        "to": recipients,
        "subject": subject,
        "text": body_plain,
    }
    status = mailgun_send(mailgun_data)

    # then notify subscribed user accounts of this event
    notify_published = EventNotifications.objects.filter(location_publish__in=[location,])
    subscribed_users = [notify.user.email for notify in notify_published]

    subject = '[' + location.email_subject_prefix + ']' + " New event: %s" % event_short_title
    from_address = location.from_email()
    plaintext = get_template('emails/new_event_announce.txt')
    htmltext = get_template('emails/new_event_announce.html')
    domain = Site.objects.get_current().domain

    c_text = {
        'event': event,
        'domain' : Site.objects.get_current().domain,
        'location': location,
    }
    text_content = plaintext.render(c_text)
    c_html = {
        'event': event,
        'domain' : Site.objects.get_current().domain,
        'location': location,
    }
    html_content = htmltext.render(c_html)

    for subscriber in subscribed_users:
        # if it's a public event, or subscriber is in the community and it's a
        # community event, then let the subscriber know. private events are not
        # announced to subscribers.
        logger.debug(event.visibility)
        try:
            u = User.objects.get(email=subscriber)
        except:
            logger.error('There was an error retrieving the user associated with email address %s, likely because the email is not unique. Skipping this notification.' % subscriber)
            return
        if (event.visibility == Event.PUBLIC) or (event.visibility == Event.COMMUNITY and u in location.residents()):
            mailgun_data={"from": from_address,
                "to": subscriber,
                "subject": subject,
                "text": text_content,
                "html": html_content,
            }
            status = mailgun_send(mailgun_data)



###############################################
########### Email Route Create ################

def create_route(route_name, route_pattern, path):
    mailgun_api_key = settings.MAILGUN_API_KEY
    list_domain = settings.LIST_DOMAIN
    # strip the initial slash
    forward_url = os.path.join(list_domain, path)
    forward_url = "https://" + forward_url
    logger.debug(forward_url)
    logger.debug(list_domain)
    expression = "match_recipient('%s')" % route_pattern
    logger.debug(expression)
    forward_url = "forward('%s')" % forward_url
    logger.debug(forward_url)
    return requests.post( "https://api.mailgun.net/v2/routes",
            auth=("api", mailgun_api_key),
            data={"priority": 1,
                "description": route_name,
                # the route pattern is a string but still needs to be quoted
                "expression": expression,
                "action": forward_url,
            }
    )

# TODO - We are goign to try and not create new routes
#def create_event_email(sender, instance, created, using, **kwargs):
#    if created == True:
#        # XXX TODO should probably hash the ID or name of the event so we're
#        # not info leaking here, if we care?
#        route_pattern = "event%d" % instance.id
#        route_name = 'Event %d' % instance.id
#        path = "events/message/"
#        resp = create_route(route_name, route_pattern, path)
#post_save.connect(create_event_email, sender=Event)

############################################
########### EMAIL ENDPOINTS ################

@csrf_exempt
def event_message(request, location_slug=None):
    ''' Message event admins and organizers via an email alias.'''
    if not request.method == 'POST':
        return HttpResponseRedirect('/404')

    recipient = request.POST.get('recipient')
    from_address = request.POST.get('from')
    sender = request.POST.get('sender')
    subject = request.POST.get('subject')
    body_plain = request.POST.get('body-plain')
    body_html = request.POST.get('body-html')

    # get the event info and make sure the event exists
    # we know that the route is always in the form eventXX, where XX is the
    # event id.
    alias = recipient.split('@')[0]
    logger.debug("event_message: alias=%s" % alias)
    event = None
    try:
        event_id = int(alias[5:])
        logger.debug("event_message: event_id=%s" % event_id)
        event = Event.objects.get(id=event_id)
    except:
        pass
    if not event:
        logger.warn("Event (%s) not found.  Exiting quietly." % alias)
        return HttpResponse(status=200)

    # Do some sanity checkint so we don't mailbomb everyone
    header_txt = request.POST.get('message-headers')
    message_headers = json.loads(header_txt)
    message_header_keys = [item[0] for item in message_headers]
    # make sure this isn't an email we have already forwarded (cf. emailbombgate 2014)
    # A List-Id header will only be present if it has been added manually in
    # this function, ie, if we have already processed this message.
    if request.POST.get('List-Id') or 'List-Id' in message_header_keys:
        logger.debug('List-Id header was found! Dropping message silently')
        return HttpResponse(status=200)
    # If 'Auto-Submitted' in message_headers or message_headers['Auto-Submitted'] != 'no':
    if 'Auto-Submitted' in message_header_keys:
        logger.info('message appears to be auto-submitted. reject silently')
        return HttpResponse(status=200)

    # find the event organizers and admins
    organizers = event.organizers.all()
    location_event_admin = EventAdminGroup.objects.get(location=event.location)
    admins = location_event_admin.users.all()

    # Build our bcc list
    bcc_list = []
    for organizer in organizers:
        if organizer.email not in bcc_list:
            bcc_list.append(organizer.email)
    for admin in admins:
        if admin.email not in bcc_list:
            bcc_list.append(admin.email)
    logger.debug("BCC List: %s" % bcc_list)

    # Make sure this person can post to our list
    if not sender in bcc_list:
        # TODO - This shoud possibly send a response so they know they were blocked
        logger.warn("Sender (%s) not allowed.  Exiting quietly." % sender)
        return HttpResponse(status=200)
    bcc_list.remove(sender)

    # prefix subject
    if subject.find('[Event Discussion') < 0:
        prefix = '[Event Discussion: %s] ' % event.slug[0:30]
        subject = prefix + subject

    # Add in footer
    #domain = Site.objects.get_current().domain
    event_url = request.build_absolute_uri(urlresolvers.reverse('gather_view_event', args=(event.location.slug, event.id, event.slug)))
    footer_msg = "You are receving this email because you are one of the organizers or an event admin at this location. Visit this event online at %s" % event_url
    body_plain = body_plain + "\n\n-------------------------------------------\n" + footer_msg
    if body_html:
        body_html = body_html + "<br><br>-------------------------------------------<br>" + footer_msg

    # send the message
    mailgun_data={"from": from_address,
        "to": [recipient, ],
        "bcc": bcc_list,
        "subject": subject,
        "text": body_plain,
        "html": body_html,
        "h:Reply-To": recipient,
        "h:List-Id": recipient,
        "h:Precedence": "list",
    }
    return mailgun_send(mailgun_data)




