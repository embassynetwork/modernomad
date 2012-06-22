from django.contrib.auth.models import User
from django.forms import CharField, ModelForm, PasswordInput
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from core.models import UserProfile, House

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password']
		widgets = {
				'password': PasswordInput(render_value=False),
				}
		password2 = CharField(widget=PasswordInput(render_value=False), 
				label=_("Password (again)"))

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


class CombinedUserForm(object):
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

	@property
	def cleaned_data(self):
		data = self.user_form.cleaned_data
		data.update(self.profile_form.cleaned_data)
		return data

class HouseForm(ModelForm):
	class Meta:
		model = House
		exclude = ['admins', 'created', 'updated']


