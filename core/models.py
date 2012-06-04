from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models


class House(models.Model):
	name = models.CharField(max_length=200)
	summary = models.CharField(max_length=200)
	created_date = models.DateTimeField('date created')
	# need custom validator for address
	address = models.CharField(max_length=400)
	amenities = models.TextField()
	house_rules = models.TextField()
	long_term_rooms = models.IntegerField()
	short_term_rooms = models.IntegerField()

	def __unicode__(self):
		return (self.name)


RESOURCE_TYPES = (
	('bedroom', 'bedroom'),
	('bed', 'bed'),
	('conference_room', 'conference room'),
)

class Resource(models.Model):
	house = models.ForeignKey(House)
	name = models.CharField(max_length=200)
	blurb = models.CharField(max_length=200)
	resource_type = models.CharField(max_length=200, choices=RESOURCE_TYPES)
	def __unicode__(self):
		return (self.name)


class UserProfile(models.Model):
	status_choices = ((u'0', 'New'), (u'1', 'Introduced'), (u'2', 'Accepted'))
	user = models.OneToOneField(User)

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	# XXX upload_to will need to be a better solution eventually (s3? mongo?) 
	image = models.ImageField(upload_to="data/avatars/%Y/%m/%d/", blank=True, help_text="Leave blank to use <a href="">Gravatar</a>")
	bio = models.TextField("A bit about yourself")
	links = models.TextField(blank=True, help_text="Comma-separated, please")
	upto = models.TextField("What are you Up To?", help_text="What are some projects you're working on? What are you up to, bigger picture?")

	# TODO (JMC): Replace with use of Django Groups
	status = models.CharField(max_length=1, choices = status_choices)
	invited_by = models.ForeignKey('self', blank=True, null=True, help_text="Your chosen reference will be asked to confirm your relationship.")

	def __unicode__(self):
		return (self.user.__unicode__())

	def save(self, *args, **kwargs):
		# for new users, set the status depending on whether they were
		# invited by someone or not
		if not self.id:
			if self.invited_by is None:
				self.status = u'0'
			else:
				self.status = u'1'
		super(UserProfile, self).save(*args, **kwargs)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
		
class Endorsement(models.Model):
	# endorsements from a person or house
	endorsee = models.ForeignKey(UserProfile)
	endorser = models.ForeignKey(House)
	comment = models.TextField()


