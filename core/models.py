from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.sites.models import Site
from django.core import urlresolvers
from PIL import Image
import os, datetime
from django.conf import settings
from django.core.files.storage import default_storage

# imports for signals
import django.dispatch 
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from django.core.mail import send_mail
from confirmation_email import confirmation_email_details
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

class Room(models.Model):

	GUEST = "guest"
	PRIVATE = "private"
	ROOM_USES = (
		(GUEST, "Guest"),
		(PRIVATE, "Private"),
	)
	name = models.CharField(max_length=200)
	default_rate = models.IntegerField()
	description = models.TextField(blank=True, null=True)
	primary_use = models.CharField(max_length=200, choices=ROOM_USES, default=PRIVATE, verbose_name='Indicate whether this room should be listed for guests to make reservations.')

	def __unicode__(self):
		return self.name

class Reservation(models.Model):
	PENDING = 'pending'
	APPROVED = 'approved'
	CONFIRMED = 'confirmed'
	HOUSE_DECLINED = 'house declined'
	CANCELED = 'canceled'
	PAID = 'paid'
	USER_DECLINED = 'user declined'

	RESERVATION_STATUSES = (
		(PENDING, 'Pending'),
		(APPROVED, 'Approved'),
		(CONFIRMED, 'Confirmed'),
		(HOUSE_DECLINED, 'House Declined'),
		(USER_DECLINED, 'User Declined'),
		(CANCELED, 'Canceled'),
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
	room = models.ForeignKey(Room, null=True)
	#accommodation_preference = models.CharField(verbose_name='Accommodation Type Preference', max_length=200, choices = ACCOMMODATION_PREFERENCES)
	tags = models.CharField(max_length =200, help_text='What are 2 or 3 tags that characterize this trip?')
	guest_emails = models.CharField(max_length=400, blank=True, null=True, 
		help_text="Comma-separated list of guest emails. A confirmation email will be sent to these guests if you fill this out. (Optional)")
	purpose = models.TextField(verbose_name='What is the purpose of the trip?')
	comments = models.TextField(blank=True, null=True, verbose_name='Any additional comments. (Optional)')

	@models.permalink
	def get_absolute_url(self):
		return ('core.views.ReservationDetail', [str(self.id)])

	def __unicode__(self):
		return "reservation %d" % self.id

	def total_nights(self):
		return (self.depart - self.arrive).days

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

Purpose of trip: %s. 

Additional Comments: %s. 

---- ABOUT THEM -----

How they heard about us: %s. 

Projects: %s.

Sharing interests: %s. 

Discussion interests: %s.


-------------------------------------

You can view, approve or deny this request at %s%s. Or email 
the requesting user at %s. 
		''' % (obj.status, obj.user.first_name, obj.user.last_name, obj.accommodation_preference, 
			str(obj.arrive), str(obj.depart), hosting_info, obj.user.profile.referral, 
			obj.user.profile.projects, obj.user.profile.sharing, obj.user.profile.discussion, 
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
	# create new reconciliation object for confirmed reservations
	if instance.status == Reservation.CONFIRMED:
		try:
			Reconcile.objects.get(reservation=instance)
		except:
			reconcile = Reconcile()
			reconcile.reservation = instance
			reconcile.save()

	# generate notification emails as appropriate
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

In the meantime, why not visit http://embassynetwork.com/calendar to check out who else will be around while you are here? 

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

class Reconcile(models.Model):
	''' The Reconcile object is automatically created when a reservation is confirmed.'''
	COMP = "comp"
	UNPAID = "unpaid"
	PAID = "paid"
	INVALID = "invalid"
	STATUSES = (
		(COMP, 'Comp'),
		(UNPAID, 'Unpaid'),
		(PAID, 'Paid'),
		(INVALID, "Invalid")
	)

	reservation = models.OneToOneField(Reservation)
	custom_rate = models.IntegerField(null=True, blank=True, help_text="If empty, the default rate for shared or private accommodation will be used.") # default as a function of reservation type
	status = models.CharField(max_length=200, choices=STATUSES, default=UNPAID)
	automatic_invoice = models.BooleanField(default=False, help_text="If True, an invoice will be sent to the user automatically at the end of their stay.")
	payment_service = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Stripe, Paypal, Dwolla, etc. May be empty")
	payment_method = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Visa, cash, bank transfer")
	paid_amount = models.IntegerField(null=True, blank=True)
	transaction_id = models.CharField(max_length=200, null=True, blank=True)
	payment_date = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return "reconcile reservation %d" % self.reservation.id
	def get_rate(self):
		if not self.custom_rate:
			return self.default_rate()
		else:
			return self.custom_rate
	get_rate.short_description = 'Rate'

	def html_color_status(self):
		if self.status == Reconcile.PAID:
			color_code = "#5fbf00"
		elif self.status == Reconcile.UNPAID:
			color_code = "#bf0000"
		elif self.status == Reconcile.COMP:
			color_code = "#ffc000"
		else:
			color_code = "#000000"
		return '<span style="color: %s;">%s</span>' % (color_code, self.status)
	html_color_status.allow_tags = True


	def default_rate(self):
		return self.reservation.room.default_rate

	def send_invoice(self):
		''' trigger a reminder email to the guest about payment.''' 
		if self.reservation.hosted:
			# XXX TODO make this a proper error which is viewable in the admin form.
			print "hosted reservation invoices not supported"
			return
		if not self.status == Reconcile.UNPAID:
			# XXX TODO eventually send an email for COMPs too, but a
			# different once, with thanks/asking for feedback.
			return

		total_owed = self.reservation.total_nights()*self.get_rate()

		plaintext = get_template('emails/invoice.txt')
		htmltext = get_template('emails/invoice.html')
		c = Context({
			'first_name': self.reservation.user.first_name, 
			'res_id': self.reservation.id,
			'today': datetime.datetime.today(), 
			'arrive': self.reservation.arrive, 
			'depart': self.reservation.depart, 
			'room': self.reservation.room.name, 
			'num_nights': self.reservation.total_nights(), 
			'rate': self.get_rate(), 
			'total': total_owed,
		}) 

		subject = "[Embassy SF] Thanks for Staying with us!" 
		sender = "stay@embassynetwork.com"
		recipients = [self.reservation.user.email,]
		text_content = plaintext.render(c)
		html_content = htmltext.render(c)
		msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
		msg.attach_alternative(html_content, "text/html")
		msg.send()

	def generate_receipt(self):
		pass

	def store_payment_details(self, transaction_id, date, method, amount, service=None):
		self.transaction_id = transaction_id
		self.payment_date = date
		self.payment_method = method
		self.amount = amount
		if service: self.payment_service = service
		self.save()

Reservation.reconcile = property(lambda r: Reconcile.objects.get_or_create(reservation=r)[0])

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

def get_default_profile_img():
	path = os.path.join(settings.MEDIA_ROOT, "data/avatars/default.jpg")
	return file(path)

class UserProfile(models.Model):
	IMG_SIZE = (300,300)
	IMG_THUMB_SIZE = (150,150)

	# User model fields: username, first_name, last_name, email, 
	# password, is_staff, is_active, is_superuser, last_login, date_joined,
	user = models.OneToOneField(User)
	updated = models.DateTimeField(auto_now=True)
	image = models.ImageField(upload_to=profile_img_upload_to, help_text="Image should have square dimensions.", default="data/avatars/default.jpg")
	image_thumb = models.ImageField(upload_to="data/avatars/%Y/%m/%d/", blank=True, null=True)
	bio = models.TextField("About you", blank=True, null=True)
	links = models.TextField(help_text="Comma-separated", blank=True, null=True)

	projects = models.TextField(verbose_name='Current Projects', help_text='Describe one or more projects you are currently working on')
	sharing = models.TextField(help_text="Is there anything you'd be interested in learning or sharing during your stay?")
	discussion = models.TextField(help_text="We like discussing thorny issues with each other. What's a question that's been on your mind lately that you don't know the answer to?")
	referral = models.CharField(max_length=200, verbose_name='How did you hear about us?')

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

	# if this is the default avatar, reuse it for the thumbnail (lazy, but only
	# for backwards compatibility for those who created accounts before images
	# were required)
	if instance.image.name == "data/avatars/default.jpg":
		instance.image_thumb = "data/avatars/default.thumb.jpg"

	elif instance.image and (obj == None or obj.image != instance.image or obj.image_thumb == None):
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

		# now delete any old images
		if obj and obj.image and obj.image.name != "data/avatars/default.jpg":
			default_storage.delete(obj.image.path)

		if obj and obj.image_thumb and obj.image_thumb.name != "data/avatars/default.thumb.jpg":
			default_storage.delete(obj.image_thumb.path)


		

