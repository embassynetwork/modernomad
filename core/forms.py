from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from PIL import Image
import os, datetime
from django.conf import settings
from django.template import Template, Context
from core.models import UserProfile, Reservation, EmailTemplate
from django.contrib.sites.models import Site

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class UserProfileForm(forms.ModelForm):     
	# this is used in the profile edit page. 
	''' This form manually incorporates the fields corresponding to the base 
	User model, associated via the UserProfile model via a OneToOne field, so 
	that both models can be updated via the same form. '''

	error_messages = {
		'password_mismatch': _("The two password fields didn't match."),
	}

	# the regex field type automatically validates the value entered against
	# the supplied regex.
	username = forms.RegexField(
		label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
		help_text = _("30 characters or fewer. Letters, digits and "
					  "@/./+/-/_ only."),
		error_messages = {
			'invalid': _("This value may contain only letters, numbers and "
						 "@/./+/-/_ characters.")})
	first_name = forms.CharField(label=_('First Name'))
	last_name = forms.CharField(label=_('Last Name'))

	email = forms.EmailField(label=_("E-mail"), max_length=75)
	password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("New Password"))
	password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), 
		label=_("New Password (again)"))

	class Meta:
		model = UserProfile
		exclude = ['user', 'status', 'image_thumb', 'customer_id', ]
		# fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'image', 'bio', 'links']

	def __init__(self, *args, **kwargs):
		super(UserProfileForm, self).__init__(*args, **kwargs)
		# self.instance will always be an instance of UserProfile. if this
		# is an existing object, then populate the initial values. 
		print self.fields['image'].required
		print self.fields['sharing'].required
		
		if self.instance.id is not None:
			# initialize the form fields with the existing values from the model.  	
			self.fields['first_name'].initial = self.instance.user.first_name
			self.fields['last_name'].initial = self.instance.user.last_name
			self.fields['username'].initial = self.instance.user.username
			self.fields['email'].initial = self.instance.user.email	

			self.fields['password1'].required = False
			self.fields['password2'].required = False


	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password2:
			if password1 != password2:
				raise forms.ValidationError(
					self.error_messages['password_mismatch'])
		return password2

	def clean_links(self):
		# validates and formats the urls, returning a string of comma-separated urls
		links = self.cleaned_data['links']
		if len(links) > 0:
			raw_link_list = links.split(',')
			# the UrlField class has some lovely validation code written already.  
			url = forms.URLField()
			cleaned_links = []
			for l in raw_link_list:
				try:
					cleaned = url.clean(l.strip())
					print cleaned 
					cleaned_links.append(cleaned)
				except forms.ValidationError:
					# customize the error raised by UrlField.
					raise forms.ValidationError('At least one of the URLs is not correctly formatted.')
			links = ", ".join(cleaned_links)
		return links

	def save(self, commit=True):
		# save the UserProfile (if editing an existing instance, it will be updated)
		profile = super(UserProfileForm, self).save()
		# then update the User model with the values provided
		user = User.objects.get(pk=profile.user.pk)
		if self.cleaned_data.get('email'):
			user.email = self.cleaned_data.get('email')
		if self.cleaned_data.get('username'):
			user.username = self.cleaned_data.get('username')
		if self.cleaned_data['first_name']:
			user.first_name = self.cleaned_data.get('first_name')
		if self.cleaned_data['last_name']:
			user.last_name = self.cleaned_data.get('last_name')
		if self.cleaned_data.get('password2'):
			# set_password hashes the selected password
			user.set_password(self.cleaned_data['password2'])
		user.save()
		return user


class ReservationForm(forms.ModelForm):
	class Meta:
		model = Reservation
		exclude = ['created', 'updated', 'user', 'last_msg', 'status']
		widgets = { 
			'arrive': forms.DateInput(attrs={'class':'datepicker'}),
			'depart': forms.DateInput(attrs={'class':'datepicker'}),
		}

#	def clean_guest_emails(self):
#		# validates guest emails, returning a string of comma-separated urls
#		emails = self.cleaned_data['guest_emails']
#		if len(emails) > 0:
#			raw_emails_list = emails.split(',')
#			# the EmailField class has some lovely validation code written already.  
#			email_field = forms.EmailField()
#			cleaned_emails = []
#			for e in raw_emails_list:
#				try:
#					cleaned = email_field.clean(e.strip(" "))
#					cleaned_emails.append(cleaned)
#				except forms.ValidationError:
#					# customize the error raised by UrlField.
#					raise forms.ValidationError('At least one of the emails is not correctly formatted.')
#			emails = ",".join(cleaned_emails)
#			print emails
#		return emails

	def clean(self):
		cleaned_data = super(ReservationForm, self).clean()
		hosted = cleaned_data.get('hosted')
		guest_name = cleaned_data.get('guest_name')
		if hosted and not guest_name:
			self._errors["guest_name"] = self.error_class(['Hosted reservations require a guest name.'])
		arrive = cleaned_data.get('arrive')
		depart = cleaned_data.get('depart')
		if (depart - arrive).days > settings.MAX_RESERVATION_DAYS:
			self._errors["depart"] = self.error_class(['Sorry! We only accept reservation requests greater than 2 weeks in special circumstances. Please limit your request to two weeks.'])
		return cleaned_data

	# XXX TODO
	# make sure depart is at least one day after arrive. 


class PaymentForm(forms.Form):
	name = forms.CharField()
	email = forms.EmailField()
	card_number = forms.CharField()
	cvc = forms.IntegerField()
	expiration_month = forms.IntegerField(label='(MM)')
	expiration_year = forms.IntegerField(label='(YYYY)')
	amount = forms.IntegerField(label="Amount in whole dollars")
	comment = forms.CharField(widget=forms.Textarea, required=False, help_text="Optional. If you are\
contributing for someone else, make sure we know who this payment is for.")

class StripeCustomerCreationForm(forms.Form):
	name = forms.CharField()
	email = forms.EmailField()
	card_number = forms.CharField()
	cvc = forms.IntegerField()
	expiration_month = forms.IntegerField(label='(MM)')
	expiration_year = forms.IntegerField(label='(YYYY)')


class EmailTemplateForm(forms.Form):
	''' We don't actually make this a model form because it's a derivative
	function of a model but not directly constructed from the model fields
	itself.''' 
	sender = forms.EmailField( widget=forms.TextInput(attrs={'readonly':'readonly'}))
	recipient = forms.EmailField() 
	footer = forms.CharField(widget=forms.Textarea(attrs={'readonly':'readonly'}))
	subject = forms.CharField()
	body = forms.CharField(widget=forms.Textarea)

	def __init__(self, tpl, reservation):
		''' pass in an EmailTemplate instance, and a reservation object '''

		domain = Site.objects.get_current().domain
		# calling super will initialize the form fields 
		super(EmailTemplateForm, self).__init__()

		# add in the extra fields
		self.fields['sender'].initial = EmailTemplate.FROM_ADDRESS
		self.fields['recipient'].initial = reservation.user.email
		self.fields['footer'].initial = forms.CharField(
				widget=forms.Textarea(attrs={'readonly':'readonly'})
			)
		self.fields['footer'].initial = '''--------------------------------\nYour reservation is from %s to %s.\nManage your reservation at http://%s%s.''' % (reservation.arrive, reservation.depart, domain, reservation.get_absolute_url())

		# both the subject and body fields expect to have access to all fields
		# associated with a reservation, so all reservation model fields are
		# passed to the template renderer, even though we don't know (and so
		# that we don't have to know) which specific fields a given template
		# wants to use). 
		
		template_variables = {
			'created': reservation.created,
			'updated': reservation.updated,
			'status': reservation.status,
			'user': reservation.user,
			'arrive': reservation.arrive, 
			'depart': reservation.depart, 
			'arrival_time': reservation.arrival_time,
			'room': reservation.room, 
			'num_nights': reservation.total_nights(), 
			'purpose': reservation.purpose,
			'comments': reservation.comments,
			'reservation_url': "https://"+domain+reservation.get_absolute_url()
		}

		self.fields['subject'].initial = EmailTemplate.SUBJECT_PREFIX + Template(tpl.subject).render(Context(template_variables))
		self.fields['body'].initial = Template(tpl.body).render(Context(template_variables))




