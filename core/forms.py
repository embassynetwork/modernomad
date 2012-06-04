from django.forms import ModelForm
from PIL import Image

from core.models import User


class SignupForm(ModelForm):
	class Meta:
		model = User
		exclude = ('status')

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



