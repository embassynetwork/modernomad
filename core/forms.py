from django.contrib.auth.models import User
from django.forms import CharField, ModelForm, PasswordInput, DateInput, DateField, Form
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from core.models import UserProfile, House, Reservation

from django.contrib.auth.forms import UserCreationForm

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

class UserForm(ModelForm):
	password2 = CharField(widget=PasswordInput(render_value=False), 
		label=_("Password (again)"))

	class Meta:
		model = User
		widgets = {
				'password': PasswordInput(render_value=False),
				}
		fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']

	def clean(self):
		'''Verify that the values entered into the two password fields match.'''
		if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_("The two password fields didn't match."))
		return self.cleaned_data

class UserProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ['user', 'status']

	def clean_links(self):
		data = self.cleaned_data['links']
		# do stuff
		return data

	def clean_image(self):
		img_path = self.cleaned_data['image']
		if img_path is not None:
			# img_path is relative to media_root
			pass
		return img_path


class CombinedUserForm(Form):
	'''A wrapper class that combines a UserForm and a UserProfile
	form, allowing the django-registration app to collect additional
	user profile information at registration time.

	WARNING(mdh): This duck-typed class is a hack.  It is fragile
	against changes to the way django-registration handles the
	registration form, and it must be used in conjunction with
	core.views.RegistrationBackend.'''

	def __init__(self, *args, **kwargs):
		self.user_form = UserForm(*args, **kwargs)
		self.profile_form = UserProfileForm(*args, **kwargs)

	def is_valid(self):
		return self.user_form.is_valid() and self.profile_form.is_valid()

	def as_table(self):
		return self.user_form.as_table()#+ self.profile_form.as_p() #table()

	def as_p(self):
		return self.user_form.as_p() + self.profile_form.as_p()

	@property
	def cleaned_data(self):
		data = self.user_form.cleaned_data
		data.update(self.profile_form.cleaned_data)
		return data


class HouseForm(ModelForm):
	class Meta:
		model = House
		exclude = ['admins', 'created', 'updated']

class ReservationForm(ModelForm):
	class Meta:
		model = Reservation
		exclude = ['created', 'updated', 'status', 'user']
		widgets = { 
			'arrive': DateInput(attrs={'class':'datepicker'}),
			'depart': DateInput(attrs={'class':'datepicker'})
		}

	# XXX TODO
	# make sure depart is at least one day after arrive. 








