from django.contrib.auth.models import User
from django import forms #import CharField, ModelForm, PasswordInput, DateInput, DateField, Form, RegexField, EmailField
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from core.models import UserProfile, House, Reservation

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class ExtendedUserCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

	def save(self, commit=True):
		# by default the UserCreationForm saves username & password info. here we 
		# override the save method to save the additional data we have gathered. 
		user = super(ExtendedUserCreationForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data["email"]
		user.save()
		return user 


# class UserForm(ModelForm):
# 	password2 = CharField(widget=PasswordInput(render_value=False), 
# 		label=_("Password (again)"))

# 	class Meta:
# 		model = User
# 		widgets = {
# 				'password': PasswordInput(render_value=False),
# 				}
# 		fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']

# 	def clean(self):
# 		print "in clean method of UserForm"
# 		# Verify that the values entered into the two password fields match.
# 		if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
# 			if self.cleaned_data['password'] != self.cleaned_data['password2']:
# 				print "password fields did not match"
# 				raise forms.ValidationError(_("The two password fields didn't match."))
# 		print "userform data being cleaned"
# 		print self.cleaned_data
# 		return self.cleaned_data

class UserProfileForm(forms.ModelForm):     
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
		help_text = _("Required. 30 characters or fewer. Letters, digits and "
					  "@/./+/-/_ only."),
		error_messages = {
			'invalid': _("This value may contain only letters, numbers and "
						 "@/./+/-/_ characters.")},
		required=False)
	first_name = forms.CharField(label=_('First Name'), required=False)
	last_name = forms.CharField(label=_('Last Name'), required=False)

	# email field validates that the value entered is a valid email. 
	email = forms.EmailField(label=_("E-mail"), max_length=75, required=False)
	password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("New Password"), required=False)
	password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), 
		label=_("New Password (again)"), required=False)

	class Meta:
		model = UserProfile
		exclude = ['user', 'status']

	def __init__(self, *args, **kwargs):
		super(UserProfileForm, self).__init__(*args, **kwargs)
		if self.instance is not None:
			# initialize the form fields with the existing values from the model.  	
			self.fields['first_name'].initial = self.instance.user.first_name
			self.fields['last_name'].initial = self.instance.user.last_name
			self.fields['username'].initial = self.instance.user.username
			self.fields['email'].initial = self.instance.user.email	

	def clean_email(self):
		pass

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
		if links is not None:
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
		return ", ".join(cleaned_links)
		

	def clean_image(self):
		img_path = self.cleaned_data['image']
		if img_path is not None:
			# resize or do other intelligent things. 
			pass
		return img_path

	def save(self, commit=True):
		# save the UserProfile (if editing an existing instance, it will be updated)
		profile = super(UserProfileForm, self).save()
		# then update the User model with the values provided
		user = User.objects.get(pk=profile.user.pk)
		if self.cleaned_data.get('email'):
			user.email = self.cleaned_data.get('email')
		if self.cleaned_data['first_name']:
			user.first_name = self.cleaned_data.get('first_name')
		if self.cleaned_data['last_name']:
			user.last_name = self.cleaned_data.get('last_name')
		if self.cleaned_data.get('password2'):
			# set_password hashes the selected password
			user.set_password(self.cleaned_data['password2'])
		user.save()


class CombinedUserForm(object):
	'''A wrapper class that combines a UserForm and a UserProfile
	form, allowing the django-registration app to collect additional
	user profile information at registration time.

	WARNING(mdh): This duck-typed class is a hack.  It is fragile
	against changes to the way django-registration handles the
	registration form, and it must be used in conjunction with
	core.views.RegistrationBackend.

	This is ONLY used for the standalone registration form right now.
	XXX TODO - don't use this form?

	'''

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		if instance is None:
			self.user_form = UserForm(*args, **kwargs)
			self.profile_form = UserProfileForm(*args, **kwargs)
		else:
			# bind the form to the instance data
			self.user_form = UserForm(instance=instance.user)
			self.profile_form = UserProfileForm(instance=instance)	

	def is_valid(self):
		# is_valid() calls the clean() method of each form.
		return self.user_form.is_valid() and self.profile_form.is_valid()

	def as_p(self):
		return self.user_form.as_p() + self.profile_form.as_p()

	@property
	def cleaned_data(self):
		# cleaned_data is only populated once is_valid() or clean() have been called. 
		data = self.user_form.cleaned_data
		data.update(self.profile_form.cleaned_data)
		return data

	def save(self, commit=True):
		self.user_form.save(commit=commit)
		self.profile_form.save(commit=commit)


class HouseForm(forms.ModelForm):
	class Meta:
		model = House
		exclude = ['admins', 'created', 'updated']

class ReservationForm(forms.ModelForm):
	class Meta:
		model = Reservation
		exclude = ['created', 'updated', 'status', 'user']
		widgets = { 
			'arrive': forms.DateInput(attrs={'class':'datepicker'}),
			'depart': forms.DateInput(attrs={'class':'datepicker'})
		}

	# XXX TODO
	# make sure depart is at least one day after arrive. 








