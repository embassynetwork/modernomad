from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from gather.models import Event
from django import forms
from lxml.html.clean import clean_html
import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

import logging

logger = logging.getLogger(__name__)

class EventForm(forms.ModelForm):
    co_organizers = forms.CharField(required=False,  widget = forms.TextInput(attrs={'class':'form-control'}), help_text = "Optionally, select other members to co-host this event (members must have an account on this site to be listed as co-organizers).")

    class Meta:
        model = Event
        exclude = ['created', 'updated', 'creator', 'attendees', 'organizers', 'status', 'admin', 'location']
        widgets = {
                'start': forms.TextInput(attrs={'class':'datepicker form-control'}),
                'end': forms.TextInput(attrs={'class':'datepicker form-control'}),
                'title': forms.TextInput(attrs={'class':'form-control'}),
                'slug': forms.TextInput(attrs={'class':'form-control'}),
                'description': forms.Textarea(attrs={'class':'form-control', 'rows': '5'}),
                'where': forms.TextInput(attrs={'class':'form-control'}),
                'limit': forms.TextInput(attrs={'class':'form-control'}),
                'organizer_notes': forms.Textarea(attrs={'class':'form-control', 'rows': 3}),
                }

    def clean_co_organizers(self):
        co_organizers_usernames = self.cleaned_data.get('co_organizers').strip(", ").split(",")
        logger.debug('here')
        logger.debug(co_organizers_usernames)
        co_organizers = []
        for username in co_organizers_usernames:
            username = username.strip()
            if not username == '':
                try:
                    co_org_user = User.objects.get(username=username)
                    co_organizers.append(User.objects.get(username=username))
                except ObjectDoesNotExist:
                    raise forms.ValidationError(
                            _('\'%s\' is not a recognized user, please remove them to save your event. Only users with existing accounts can be listed as co-organizers (but you can always add them later!)' % username),
                        )
        return co_organizers

    def clean_description(self):
        description = self.cleaned_data.get('description')
        # sanitize the html, make sure evil things are removed.
        cleaned = clean_html(description)
        # clean_html creates a rooted html tree and wraps the content in divs
        # if they're not already present. this can create weirdness when people
        # aren't expecting it and editing the html directly in the textarea,
        # and since the template will provide markup around the text anyway, we
        # remove the wrapping div tags.
        cleaned = re.sub('^<div>', '', cleaned)
        cleaned = re.sub('</div>', '', cleaned)
        return cleaned


class EmailTemplateForm(forms.Form):
    ''' We don't actually make this a model form because it's a derivative
    function of a model but not directly constructed from the model fields
    itself.'''
    sender = forms.EmailField(widget=forms.TextInput(attrs={'readonly':'readonly', 'class':"form-control", 'type': 'hidden'}))
    recipient = forms.EmailField(widget=forms.TextInput(attrs={'class':"form-control", 'type': 'hidden'}))
    footer = forms.CharField( widget=forms.Textarea(attrs={'readonly':'readonly', 'class':"form-control"}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class':"form-control"}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class':"form-control"}))


class EventEmailTemplateForm(EmailTemplateForm):

    def __init__(self, event, location):
        ''' pass in an event and a location to use in constructing the email. '''

        domain = Site.objects.get_current().domain
        # calling super will initialize the form fields
        super(EventEmailTemplateForm, self).__init__()

        # add in the extra fields
        self.fields['sender'].initial = location.from_email()
        self.fields['footer'].initial = forms.CharField(
                widget=forms.Textarea(attrs={'readonly':'readonly'})
            )
        path = reverse('gather_view_event', args=(location.slug, event.id, event.slug))
        self.fields['footer'].initial = '''--------------------------------\nThis message was sent to attendees of the event '%s' at %s. You can view event details and update your RSVP status on the event page https://%s/%s.''' % (event.title, location.name, domain, path)

        # the recipients will be *all* the event attendees
        self.fields['recipient'].initial = ", ".join([attendee.email for attendee in list(event.attendees.all())])

        self.fields['subject'].initial = '['+location.email_subject_prefix+'] Update for event "' + event.title + '"'


