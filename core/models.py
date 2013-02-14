from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.sites.models import Site
from django.core import urlresolvers
from PIL import Image
import os
from django.conf import settings
from django.core.files.storage import default_storage

# imports for signals
import django.dispatch 
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from django.core.mail import send_mail
from confirmation_email import confirmation_email_details




class House(models.Model):
	# meta
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	admins = models.ManyToManyField(User, blank=True, null=True)
	# location
	address = models.CharField(max_length=400, unique=True)
	latLong = models.CharField(max_length=100, unique=True)
	# community size
	residents = models.IntegerField() 
	rooms = models.IntegerField() 
	# descriptive
	name = models.CharField(max_length=200) # required
	picture = models.ImageField(upload_to="photos/%Y/%m/%d", blank=True, null=True)
	description = models.TextField(max_length=2000, null=True, blank=True) # + suggested max length. possible things to incl. are description of mission/values, house rules etc. if desired. 
	mission_values = models.TextField(max_length=2000, null=True, blank=True) # comma separated list of tags
	amenities = models.TextField(blank=True, null=True)
	guests = models.NullBooleanField(blank=True, null=True)
	events = models.NullBooleanField(blank=True, null=True)
	events_description = models.TextField(blank=True, null=True)
	space_share = models.NullBooleanField(blank=True, null=True)
	space_share_description = models.TextField(blank=True, null=True)
	slug = models.CharField(max_length=100, unique=True, blank=True, null=True)
	contact_ok = models.NullBooleanField(blank=True, null=True)
	contact = models.EmailField(blank=True, null=True) # required if contact_ok = True
	# social
	website = models.URLField(verify_exists = True, null=True, blank=True, unique=True)
	twitter_handle = models.CharField(max_length=100, null=True, blank=True)
	pictures_feed = models.CharField(max_length=400, null=True, blank=True)

	# future - mailing lists?
	# deprecated: 
	# get_in_touch = models.CharField(max_length=100, unique=True, blank=True, null=True) --> replace with "ok to contact?" + email addy
	# house_rules = models.TextField(blank=True, null=True) 

	def __unicode__(self):
		if self.name:
			return (self.name)
		else:
			return self.address

RESOURCE_TYPES = (
	('private', 'private'),
	('hostel', 'hostel'),
	('conference_room', 'conference room'),
)

class Resource(models.Model):
	house = models.ForeignKey(House)
	name = models.CharField(max_length=200)
	description = models.TextField()
	resource_type = models.CharField(max_length=200, choices=RESOURCE_TYPES)
	def __unicode__(self):
		return (self.name)


class Reservation(models.Model):
	PENDING = 'pending'
	APPROVED = 'approved'
	CONFIRMED = 'confirmed'
	HOUSE_DECLINED = 'house declined'
	DELETED = 'deleted'
	PAID = 'paid'
	USER_DECLINED = 'user declined'

	PRIVATE = 'private'
	SHARED = 'shared'
	PREFER_SHARED = 'prefer shared'
	PREFER_PRIVATE = 'prefer private'

	RESERVATION_STATUSES = (
		(PENDING, 'Pending'),
		(APPROVED, 'Approved'),
		(CONFIRMED, 'Confirmed'),
		(PAID, 'Paid'),
		(HOUSE_DECLINED, 'House Declined'),
		(USER_DECLINED, 'User Declined'),
		(DELETED, 'Deleted'),
	)

	ACCOMMODATION_PREFERENCES = (
		(PRIVATE, 'Private (typical rate: $120/night)'),
		(SHARED, 'Shared (typical rate: $35/night)'),
		(PREFER_SHARED, 'Prefer shared but will take either'),
		(PREFER_PRIVATE, 'Prefer private but will take either')
	)

	# hosted reservations - only exposed to house_admins. form fields are
	# rendered in the order they are declared in the model, so leave this
	# order as-is for these fields to appear at the top of the creation and
	# edit forms.
	hosted = models.BooleanField(default=False, help_text="Hosting a guest who doesn't have an account.")
	guest_name = models.CharField(max_length=200, help_text="Guest name if you are hosting.", blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=200, choices=RESERVATION_STATUSES, default=PENDING, blank=True)
	user = models.ForeignKey(User)
	arrive = models.DateField(verbose_name='Arrival Date')
	depart = models.DateField(verbose_name='Departure Date')
	arrival_time = models.CharField(help_text='Optional, if known', max_length=200, blank=True, null=True)
	accommodation_preference = models.CharField(verbose_name='Accommodation Type Preference', max_length=200, choices = ACCOMMODATION_PREFERENCES)
	tags = models.CharField(max_length =200, help_text='What are 2 or 3 tags that characterize this trip?')
	guest_emails = models.CharField(max_length=400, blank=True, null=True, 
		help_text="Comma-separated list of guest emails. A confirmation email will be sent to your guest(s) if you fill this out. (Optional)")

	projects = models.TextField(verbose_name='Current Projects', help_text='Describe one or more projects you are currently working on')
	sharing = models.TextField(help_text="Is there anything you'd be interested in learning or sharing while you are here?")
	discussion = models.TextField(help_text="We like discussing thorny issues with each other. What's a question that's been on your mind lately that you don't know the answer to?")
	purpose = models.TextField(verbose_name='What are you in town for?')
	referral = models.CharField(max_length=200, verbose_name='How did you hear about us?')
	comments = models.TextField(blank=True, null=True, verbose_name='Any additional comments')

	@models.permalink
	def get_absolute_url(self):
		return ('core.views.ReservationDetail', [str(self.id)])

	def __unicode__(self):
		return "reservation %d" % self.id

# send house_admins notification of new reservation. use the post_save signal
# so that a) we can be sure the reservation was successfully saved, and b) the
# unique ID of this reservation only exists post-save.
@receiver(post_save, sender=Reservation)
def notify_house_admins(sender, instance, **kwargs):
	if kwargs['created'] == True:
		obj = Reservation.objects.get(pk=instance.pk)
		house_admins = User.objects.filter(groups__name='house_admin')

		subject = "[Embassy SF] Reservation Request, %s %s, %s - %s" % (obj.user.first_name, 
			obj.user.last_name, str(obj.arrive), str(obj.depart))
		sender = "stay@embassynetwork.com"
		domain = Site.objects.get_current().domain
		hosting_info = ""
		if obj.hosted:
			hosting_info = " for guest %s" % obj.guest_name
		admin_path = urlresolvers.reverse('admin:core_reservation_change', args=(obj.id,))
		message = '''Howdy, 

A new reservation has been submitted. The current status of this reservation 
is %s. You can reply-all to discuss this reservation with other house admins. 

--------------------------------------------------- 

%s %s requests %s accommodation from %s to %s%s. 


How they heard about us: %s. 

Projects: %s.

Sharing interests: %s. 

Discussion interests: %s.

Purpose of trip: %s. 

Additional Comments: %s. 

-------------------------------------

You can view, approve or deny this request at %s%s. Or email 
the requesting user at %s. 
		''' % (obj.status, obj.user.first_name, obj.user.last_name, obj.accommodation_preference, 
			str(obj.arrive), str(obj.depart), hosting_info, obj.referral, obj.projects, obj.sharing, obj.discussion, 
			obj.purpose, obj.comments, domain, admin_path, obj.user.email)
		recipients = []
		for admin in house_admins:
			recipients.append(admin.email)
		# send mail to all house admins at once; this way hose admins can
		# reply-all and discuss the application if desired. TODO should
		# probably have a mail agent handle this
		send_mail(subject, message, sender, recipients)


# define a signal for reservation approval
reservation_approved = django.dispatch.Signal(providing_args=["url", "reservation"])

@receiver(pre_save, sender=Reservation)
def detect_changes(sender, instance, **kwargs):
	try:
		obj = Reservation.objects.get(pk=instance.pk)
	except Reservation.DoesNotExist:
		obj = None
	if not instance.hosted and obj and obj.status == Reservation.PENDING and instance.status == Reservation.APPROVED:
		reservation_approved.send(sender=Reservation, url=instance.get_absolute_url, reservation = instance)
	# if the status was changed from anything else to 'confirmed', generate an email
	elif (obj == None or obj.status != Reservation.CONFIRMED) and instance.status == Reservation.CONFIRMED:
		subject = "[Embassy SF] Reservation Confirmation, %s - %s" % (str(instance.arrive), 
		str(instance.depart))
		sender = "stay@embassynetwork.com"
		domain = 'http://' + Site.objects.get_current().domain
		house_info_url = domain + '/guestinfo/'
		recipients = []
		# take the contents of the new instance over the old instance, if necessary. 
		if instance.guest_emails:
			recipients += instance.guest_emails.split(",") 
		# don't send confirmation emails to hosts 
		if not instance.hosted:
			recipients.append(instance.user.email)
		print recipients
		if len(recipients) > 0:

			text = '''Dear %s,

This email confirms we will see you from %s - %s. Information on accessing the
house, house norms, and transportation can be viewed online at %s, and for
your convenience is also included below. View or edit your reservation by logging 
into %s. 

Let us know if you have any questions.
Thanks and see you soon!

-------------------------------------------------------------------------------

''' % (instance.user.first_name.title(), instance.arrive, instance.depart, house_info_url, domain)
			text += confirmation_email_details
			send_mail(subject, text, sender, recipients) 


# XXX do we even need a second signal?
@receiver(reservation_approved, sender=Reservation)
def approval_notify(sender, url, reservation, **kwargs):
	recipient = [reservation.user.email]
	subject = "[Embassy SF] Reservation Approval"
	domain = Site.objects.get_current().domain
	message = "Your reservation request for %s - %s has been approved. You must confirm this reservation to finalize!\n\nView your reservation details and confirm at %s%s" % (
		str(reservation.arrive), str(reservation.depart), domain, reservation.get_absolute_url())
	sender = "stay@embassynetwork.com"
	send_mail(subject, message, sender, recipient)


def profile_img_upload_to(instance, filename):
	upload_path = "data/avatars/%s/" % instance.user.username
	upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
	print upload_path
	print upload_abs_path
	print filename
	print "*****"
	if not os.path.exists(upload_abs_path):
		os.makedirs(upload_abs_path)
	return upload_path

class UserProfile(models.Model):
	IMG_SIZE = (300,300)
	IMG_THUMB_SIZE = (150,150)

	# User model fields: username, first_name, last_name, email, 
	# password, is_staff, is_active, is_superuser, last_login, date_joined,
	user = models.OneToOneField(User)
	updated = models.DateTimeField(auto_now=True)
	image = models.ImageField(upload_to=profile_img_upload_to, blank=True, null=True, help_text="Image should have square dimensions.")
	image_thumb = models.ImageField(upload_to="data/avatars/%Y/%m/%d/", blank=True, null=True)
	bio = models.TextField("About you", blank=True, null=True)
	links = models.TextField(help_text="Comma-separated", blank=True, null=True)

	def __unicode__(self):
		return (self.user.__unicode__())

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

@receiver(pre_save, sender=UserProfile)
def size_images(sender, instance, **kwargs):
	try:
		obj = UserProfile.objects.get(pk=instance.pk)
	except UserProfile.DoesNotExist:
		# if the reservation does not exist yet, then it's new. 
		obj = None
	if instance.image and (obj == None or obj.image != instance.image or obj.image_thumb == None):
		im = Image.open(instance.image)
		img_upload_dir_rel = profile_img_upload_to(instance, instance.image.name)
		main_img_full_path = os.path.join(settings.MEDIA_ROOT, img_upload_dir_rel, instance.image.name)
		# resize returns a copy. resize() forces the dimensions of the image
		# to match SIZE specified, squeezing the image if necessary along one
		# dimension.
		main_img = im.resize(UserProfile.IMG_SIZE, Image.ANTIALIAS)
		main_img.save(main_img_full_path)
		main_img_rel_path = os.path.join(img_upload_dir_rel, instance.image.name)
		instance.image = main_img_rel_path
		# now use resize this to generate the smaller thumbnail
		thumb_img = im.resize(UserProfile.IMG_THUMB_SIZE, Image.ANTIALIAS)
		thumb_full_path = os.path.splitext(main_img_full_path)[0] + ".thumb" + os.path.splitext(main_img_full_path)[1]
		thumb_img.save(thumb_full_path)
		# the ImageFileField needs the path info relative to the media
		# directory
		# XXX Q: does this save the file twice? once by PIL and another time
		# reading it in and saving it to the same place when the model saves?
		thumb_rel_path = os.path.join(img_upload_dir_rel, os.path.basename(thumb_full_path))
		instance.image_thumb = thumb_rel_path
		print thumb_rel_path	
		# now delete the old images
		if obj.image:
			default_storage.delete(obj.image.path)
		if obj.image_thumb:
			default_storage.delete(obj.image_thumb.path)

	if obj and obj.image and not instance.image:
		# if the user deleted their profile image, unlink thumbnail and remove the images. 
		instance.image_thumb = None	
		default_storage.delete(obj.image.path)
		default_storage.delete(obj.image_thumb.path)
		

