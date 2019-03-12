import uuid
import os
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from modernomad.core.models import Location


logger = logging.getLogger(__name__)


class EventAdminGroup(models.Model):
    ''' Define admininstrative groups per location.'''
    location = models.OneToOneField(Location, related_name="event_admin_group")
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.location.name + " Admin Group"

    class Meta:
        app_label = 'gather'


class EventSeries(models.Model):
    ''' Events may be associated with a series. A series has a name and
    desciption, and its own landing page which lists the associated events. '''
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'gather'


def event_img_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # rename file to random string
    filename = "%s.%s" % (uuid.uuid4(), ext.lower())

    upload_path = "events/"
    upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    if not os.path.exists(upload_abs_path):
        os.makedirs(upload_abs_path)
    return os.path.join(upload_path, filename)


class EventManager(models.Manager):
    def upcoming(self, upto=None, current_user=None, location=None):
        # return the events happening today or in the future, returning up to
        # the number of events specified in the 'upto' argument.
        today = timezone.now()
        logger.debug(today)
        qs = super().get_queryset()
        upcoming = qs.filter(end__gte=today).exclude(
            status=Event.CANCELED
        ).order_by('start')

        if location:
            upcoming = upcoming.filter(location=location)

        viewable_upcoming = []
        for event in upcoming:
            if event.is_viewable(current_user):
                viewable_upcoming.append(event)
                if upto and len(viewable_upcoming) == upto:
                    break
        logger.debug(viewable_upcoming)
        return viewable_upcoming

    class Meta:
        app_label = 'gather'


class Event(models.Model):
    PENDING = 'waiting for approval'
    FEEDBACK = 'seeking feedback'
    READY = 'ready to publish'
    LIVE = 'live'
    CANCELED = 'canceled'

    event_statuses = (
            (PENDING, 'Waiting for Approval'),
            (FEEDBACK, 'Seeking Feedback'),
            (READY, 'Ready to publish'),
            (LIVE, 'Live'),
            (CANCELED, 'Canceled'),
    )

    PUBLIC = 'public'
    PRIVATE = 'private'
    COMMUNITY = 'community'

    event_visibility = (
            (PUBLIC, 'Public'),
            (PRIVATE, 'Private'),
            (COMMUNITY, 'Community')
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    start = models.DateTimeField(verbose_name="Start time")
    end = models.DateTimeField(verbose_name="End time")
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=60, help_text="This will be auto-suggested based on the event title, but feel free to customize it.", unique=True)
    description = models.TextField(help_text="Basic HTML markup is supported for your event description.")
    image = models.ImageField(upload_to=event_img_upload_to)
    attendees = models.ManyToManyField(User, related_name="events_attending", blank=True)
    notifications = models.BooleanField(default=True)
    # where, site, place, venue
    where = models.CharField(verbose_name='Where will the event be held?', max_length=500, help_text="Either a specific room at this location or an address if elsewhere")
    creator = models.ForeignKey(User, related_name="events_created")
    organizers = models.ManyToManyField(User, related_name="events_organized", blank=True)
    organizer_notes = models.TextField(blank=True, null=True, help_text="These will only be visible to other organizers")
    limit = models.IntegerField(default=0, help_text="Specify a cap on the number of RSVPs, or 0 for no limit.", blank=True)
    visibility = models.CharField(choices=event_visibility, max_length=200, default=PUBLIC, help_text="Community events are visible only to community members. Private events are visible to those who have the link.")  # noqa
    status = models.CharField(choices=event_statuses, default=PENDING, max_length=200, verbose_name='Review Status', blank=True)
    endorsements = models.ManyToManyField(User, related_name="events_endorsed", blank=True)
    # the location field is optional but lets you associate an event with a
    # specific location object that is also managed by this software. a single
    # location or multiple locations can be defined.
    location = models.ForeignKey(Location)
    series = models.ForeignKey(EventSeries, related_name='events', blank=True, null=True)
    admin = models.ForeignKey(EventAdminGroup, related_name='events')

    objects = EventManager()

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'gather'

    def is_viewable(self, current_user):
        '''an event is viewable if it's both live and public, OR if it's a
        community event and the user is a member of the community, OR the
        current_user is a community event admin, registered attendee or
        organizer.'''

        # check some priveleges first...
        if (self.admin and current_user) and (current_user in self.admin.users.all()):
            is_event_admin = True
        else:
            is_event_admin = False

        if current_user and current_user in self.location.residents():
            is_community_member = True
        else:
            is_community_member = False

        # ok now let's see...
        can_view = any([
            self.status == 'live' and self.visibility == Event.PUBLIC,
            is_event_admin,
            current_user == self.creator,
            current_user in self.organizers.all(),
            current_user in self.attendees.all(),
            is_community_member and self.visibility != Event.PRIVATE

        ])

        if can_view:
            viewable = True
        else:
            viewable = False
        return viewable


def default_event_status(sender, instance, created, using, **kwargs):
    logger.debug(instance)
    logger.debug(created)
    logger.debug(instance.status)

    if created:
        if instance.creator in instance.admin.users.all():
            instance.status = Event.FEEDBACK
        else:
            instance.status = Event.PENDING


post_save.connect(default_event_status, sender=Event)


class EventNotifications(models.Model):
    user = models.OneToOneField(User, related_name='event_notifications')
    # send reminders on day-of the event?
    reminders = models.BooleanField(default=True)
    # receive weekly announcements about upcoming events?
    location_weekly = models.ManyToManyField(Location, related_name="weekly_event_notifications")
    location_publish = models.ManyToManyField(Location, related_name="event_published")

    class Meta:
        app_label = 'gather'


User.event_notifications = property(lambda u: EventNotifications.objects.get_or_create(user=u)[0])


# override the save method of the User model to create the EventNotifications
# object automatically for new users
def add_user_event_notifications(sender, instance, created, using, **kwargs):
    # just accessing the field will create the object, since the field is
    # defined with get_or_create, above.
    instance.event_notifications
    return
