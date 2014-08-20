from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from PIL import Image
import os, datetime
from django.conf import settings
from django.template import Template, Context
from core.models import UserProfile, Reservation, EmailTemplate, Room
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
						 "@/./+/-/_ characters.")}, widget=forms.TextInput(attrs={'class':'form-control'}))
	first_name = forms.CharField(label=_('First Name'), widget= forms.TextInput(attrs={'class':'form-control'}))
	last_name = forms.CharField(label=_('Last Name'), widget= forms.TextInput(attrs={'class':'form-control'}))

	email = forms.EmailField(label=_("E-mail"), max_length=75, widget= forms.TextInput(attrs={'class':'form-control'}))
	password1 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class':'form-control'}), label=_("New Password"))
	password2 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class':'form-control'}), label=_("New Password (again)"))

	class Meta:
		model = UserProfile
		exclude = ['user', 'status', 'image_thumb', 'customer_id', ]
		# fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'image', 'bio', 'links']
		widgets = {
			'bio': forms.Textarea(attrs={'class':'form-control', 'rows': '3'}),
			'links': forms.TextInput(attrs={'class':'form-control'}),
			'projects': forms.Textarea(attrs={'class':'form-control', 'rows': '3'}),
			'sharing': forms.Textarea(attrs={'class':'form-control', 'rows': '3'}),
			'discussion': forms.Textarea(attrs={'class':'form-control', 'rows': '3'}),
			'referral': forms.TextInput(attrs={'class':'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		super(UserProfileForm, self).__init__(*args, **kwargs)

		# image data is processed in the save method 
		self.fields['image'].required = False

		# self.instance will always be an instance of UserProfile. if this
		# is an existing object, then populate the initial values. 
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

	def clean_username(self):
		username = self.cleaned_data['username']
		if not self.instance.id:
			if username and User.objects.filter(username=username):
				raise forms.ValidationError('There is already a user with this username. If this is your account and you need to recover your password, you can do so from the login page.')
		return username

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
					#print cleaned 
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
		exclude = ['created', 'updated', 'user', 'last_msg', 'status', 'location']
		widgets = { 
			'arrive': forms.DateInput(attrs={'class':'datepicker form-control'}),
			'depart': forms.DateInput(attrs={'class':'datepicker form-control'}),
		}

	def __init__(self, location, *args, **kwargs):
		super(ReservationForm, self).__init__(*args, **kwargs)
		self.location = location
		self.fields['room'].queryset = Room.objects.filter(location=location).filter(primary_use="guest")

	def clean(self):
		cleaned_data = super(ReservationForm, self).clean()
		arrive = cleaned_data.get('arrive')
		depart = cleaned_data.get('depart')
		if (depart - arrive).days > self.location.max_reservation_days:
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
	sender = forms.EmailField( widget=forms.TextInput(attrs={'readonly':'readonly', 'class':"form-control"}))
	recipient = forms.EmailField(widget=forms.TextInput(attrs={'class':"form-control"}))
	footer = forms.CharField( widget=forms.Textarea(attrs={'readonly':'readonly', 'class':"form-control"}))
	subject = forms.CharField(widget=forms.TextInput(attrs={'class':"form-control"}))
	body = forms.CharField(widget=forms.Textarea(attrs={'class':"form-control"}))

	def __init__(self, tpl, reservation, location):
		''' pass in an EmailTemplate instance, and a reservation object '''

		domain = Site.objects.get_current().domain
		# calling super will initialize the form fields 
		super(EmailTemplateForm, self).__init__()

		# add in the extra fields
		self.fields['sender'].initial = location.from_email()
		self.fields['recipient'].initial = reservation.user.email
		self.fields['footer'].initial = forms.CharField(
				widget=forms.Textarea(attrs={'readonly':'readonly'})
			)
		self.fields['footer'].initial = '''--------------------------------\nYour reservation is from %s to %s.\nManage your reservation at https://%s%s.''' % (reservation.arrive, reservation.depart, domain, reservation.get_absolute_url())

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
			'welcome_email_days_ahead': location.welcome_email_days_ahead,
			'reservation_url': "https://"+domain+reservation.get_absolute_url()
		}

		self.fields['subject'].initial = '['+location.email_subject_prefix+']' + Template(tpl.subject).render(Context(template_variables))
		self.fields['body'].initial = Template(tpl.body).render(Context(template_variables))


