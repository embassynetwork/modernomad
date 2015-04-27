from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gather.models import Event
from django import forms
from lxml.html.clean import clean_html
import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

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
		print 'here'
		print co_organizers_usernames
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

class NewUserForm(UserCreationForm):
	''' a new user creation form which uses the basic django user model, but requires the email to be provided. '''
	email = forms.EmailField(required=True, widget = forms.TextInput(attrs={'class':'form-control'}))
	first_name = forms.CharField(required=True,  widget = forms.TextInput(attrs={'class':'form-control'}))
	last_name = forms.CharField(required=True, widget = forms.TextInput(attrs={'class':'form-control'}))
	username = forms.RegexField(
			required=True, max_length=30, regex=r"^[\w.@+-]+$",	
			error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."},
			widget = forms.TextInput(attrs={'class':'form-control'}), 
			help_text="30 characters or fewer. Letters, digits and @/./+/-/_ only")
	password1 = forms.CharField(label="Password", required=True, widget = forms.PasswordInput(attrs={'class':'form-control'}))
	password2 = forms.CharField(label="Confirm Password", required=True, widget = forms.PasswordInput(attrs={'class':'form-control'}))

	class Meta:
		model = User
		fields = ("first_name", "last_name", "username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data["email"]
		user.first_name = self.cleaned_data["first_name"]
		user.last_name = self.cleaned_data["last_name"]
		if commit:
			user.save()
		return user

