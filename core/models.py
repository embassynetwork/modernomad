from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.sites.models import Site
from django.core import urlresolvers
from PIL import Image
import os, datetime
from django.conf import settings
from django.core.files.storage import default_storage
import uuid
import stripe

# imports for signals
import django.dispatch 
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

# mail imports
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
	cancellation_policy = models.CharField(max_length=400, default="24 hours")
	shared = models.BooleanField(default=False, verbose_name="Is this room a hostel/shared accommodation?")

	def __unicode__(self):
		return self.name

class Reservation(models.Model):

	class ResActionError(Exception):
		def __init__(self, value):
			self.value = value
		def __str__(self):
			return repr(self.value)


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
	tags = models.CharField(max_length =200, help_text='What are 2 or 3 tags that characterize this trip?')
	guest_emails = models.CharField(max_length=400, blank=True, null=True, 
		help_text="Comma-separated list of guest emails. A confirmation email will be sent to these guests if you fill this out. (Optional)")
	purpose = models.TextField(verbose_name='What is the purpose of the trip?')
	comments = models.TextField(blank=True, null=True, verbose_name='Any additional comments. (Optional)')
	last_msg = models.DateTimeField(blank=True, null=True)

	@models.permalink
	def get_absolute_url(self):
		return ('core.views.ReservationDetail', [str(self.id)])

	def __unicode__(self):
		return "reservation %d" % self.id

	def total_nights(self):
		return (self.depart - self.arrive).days
	total_nights.short_description = "Nights"

	def confirm_and_notify (self):
		if not self.user.profile.customer_id:
			raise self.ResActionError("Cannot confirm a reservation without payment details.")
	
		self.status = Reservation.CONFIRMED
		self.last_msg = datetime.datetime.now()
		self.save()
		subject = "[Embassy SF] Your Reservation has been confirmed"
		domain = Site.objects.get_current().domain
		message = "Hello %s! Your reservation for %s - %s has been confirmed. We will use the payment details on file to charge your credit card at the end of your stay.\n\nAs a reminder, the cancellation policy for the %s is %s. You can always view, update, or cancel your reservation online at %s%s.\n\nThanks, and we look forward to having you!" % (self.user.first_name, str(self.arrive), str(self.depart), self.room.name, self.room.cancellation_policy, domain, self.get_absolute_url())
		recipient = [self.user.email]
		sender = "stay@embassynetwork.com"
		send_mail(subject, message, sender, recipient)

	def set_tentative_and_prompt(self):
		# approve the reservation and prompt the user to enter payment info.
		self.status = Reservation.APPROVED
		self.last_msg = datetime.datetime.today()
		self.save()

		recipient = [self.user.email]
		subject = "[Embassy SF] Action Required to Confirm your Reservation"
		domain = Site.objects.get_current().domain
		message = "Your reservation request for %s - %s has been approved.\n\nWe request that you a credit card to secure your reservation. Please visit %s%s to add a payment method.\n\nThanks so much, and we look forward to having you!" % (
			str(self.arrive), str(self.depart), domain, self.get_absolute_url())
		sender = "stay@embassynetwork.com"
		send_mail(subject, message, sender, recipient)

	def remind_payment_info_needed(self):
		# remind the user about the status of their reservation when an action
		# is required by them. (eg. if approved with payment details or if
		# confirmed without). mostly useful for legacy reservations but
		# possible this state would crop up in other situations. 
		if not ((self.status == Reservation.CONFIRMED or 
			self.status == Reservation.APPROVED) and not self.user.profile.customer_id):
			raise self.ResActionError("Reservation must be either approved or confirmed, and payment details must not already exist") 

		if self.status == Reservation.CONFIRMED:
			self.status = Reservation.APPROVED
			self.save()

		domain = Site.objects.get_current().domain
		subject = "[Embassy SF] Reminder: Action Required for your Reservation"
		message = "Hello %s! This is just a reminder that we request a credit card to secure your reservation from %s - %s. Please visit %s%s to add a payment method, otherwise we may make the room available to other guests.\n\nThank you and we look forward to having you!" % (self.user.first_name, str(self.arrive), str(self.depart), domain, self.get_absolute_url())
		recipient = [self.user.email]
		sender = "stay@embassynetwork.com"
		send_mail(subject, message, sender, recipient)

		self.last_msg = datetime.datetime.today()
		self.save()

	def remind_to_confirm(self):
		# useful for approved reservation that DO have payment info or COMPS. 
		# ie, if reservation is approved and we DO have payment info, this can
		# make it ambiguous if they want the room for sure or not. can
		# also be used for comp reservations when we don't have the payment
		# info to hold them accountable. 
		domain = Site.objects.get_current().domain
		subject = "[Embassy SF] Reminder: Action Required for your Reservation"
		message = "Hello %s! This is just a reminder to confirm (or decline) your reservation for %s - %s so that we can make the room available to others if you no longer need it. Please visit %s%s to update your reservation status. Thanks, and we look forward to having you!" % (self.user.first_name, str(self.arrive), str(self.depart), domain, self.get_absolute_url())
		recipient = [self.user.email]
		sender = "stay@embassynetwork.com"
		send_mail(subject, message, sender, recipient)
		self.last_msg = datetime.datetime.today()
		self.save()

	def comp_confirm_and_notify(self):
		if self.reconcile.status != Reconcile.COMP:
			raise ResActionError("Reservation is not marked as complimentary.")
		self.status = Reservation.CONFIRMED
		self.last_msg = datetime.datetime.now()
		self.save()
		self.comp_notify()

	def comp_notify(self):
		# send a notification to the user that their reservation has been made
		# complimentary, and ask them to let us know if anything changes. 
		if self.reconcile.status != Reconcile.COMP:
			raise ResActionError("Reservation is not marked as complimentary.")

		subject = "[Embassy SF] You've been offered a Complimentary Stay!"
		domain = Site.objects.get_current().domain
		message = "Hello %s! You have been offered a complimentay stay for your reservation %s - %s. We're excited to have you!\n\nIf you no longer need this reservation, please let us know or visit %s%s to update or cancel your reservation, so that we can make the space available to someone else. Thanks, and we look forward to having you!" % (self.user.first_name, str(self.arrive), str(self.depart), domain, self.get_absolute_url())
		recipient = [self.user.email]
		sender = "stay@embassynetwork.com"
		send_mail(subject, message, sender, recipient)

	def cancel(self):
		# cancel this reservation. make sure to update the associated reconcile
		# info. 
		self.status = Reservation.CANCELED
		self.save()
		reconcile = self.reconcile
		reconcile.status = Reconcile.INVALID
		reconcile.save()


# send house_admins notification of new reservation. use the post_save signal
# so that a) we can be sure the reservation was successfully saved, and b) the
# unique ID of this reservation only exists post-save.
@receiver(post_save, sender=Reservation)
def notify_house_admins(sender, instance, **kwargs):
	if kwargs['created'] == True:
		obj = Reservation.objects.get(pk=instance.pk)
		house_admins = User.objects.filter(groups__name='house_admin')

		domain = Site.objects.get_current().domain
		if obj.hosted:
			hosting_info = " for guest %s" % obj.guest_name
			subject = "[Embassy SF] New Reservation: %s hosting %s from %s - %s" % (obj.user.first_name, 
				obj.guest_name, str(obj.arrive), str(obj.depart))
		else:
			hosting_info = ""
			subject = "[Embassy SF] Reservation Request, %s %s, %s - %s" % (obj.user.first_name, 
			obj.user.last_name, str(obj.arrive), str(obj.depart))

		plaintext = get_template('emails/newreservation.txt')
		htmltext = get_template('emails/newreservation.html')

		c = Context({
			'status': obj.status, 
			'user_image' : "https://" + domain+ str(obj.user.profile.image_thumb),
			'first_name': obj.user.first_name, 
			'last_name' : obj.user.last_name, 
			'room_name' : obj.room.name, 
			'arrive' : str(obj.arrive), 
		 	'depart' : str(obj.depart), 
			'hosting': hosting_info, 
			'purpose': obj.purpose, 
			'comments' : obj.comments, 
			'bio' : obj.user.profile.bio,
			'referral' : obj.user.profile.referral, 
			'projects' : obj.user.profile.projects, 
			'sharing': obj.user.profile.sharing, 
			'discussion' : obj.user.profile.discussion, 
			"admin_url" : "http://" + domain + urlresolvers.reverse('reservation_manage', args=(obj.id,))

		})

		subject = "[Embassy SF] Reservation Request, %s %s, %s - %s" % (obj.user.first_name, 
			obj.user.last_name, str(obj.arrive), str(obj.depart))
		sender = "stay@embassynetwork.com"
		recipients = []
		for admin in house_admins:
			recipients.append(admin.email)
		text_content = plaintext.render(c)
		html_content = htmltext.render(c)
		msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
		msg.attach_alternative(html_content, "text/html")
		msg.send()

class Reconcile(models.Model):
	''' The Reconcile object is automatically created when a reservation is confirmed.'''
	COMP = "comp"
	UNPAID = "unpaid"
	INVOICED = "invoiced"
	PAID = "paid"
	INVALID = "invalid"
	STATUSES = (
		(COMP, 'Comp'),
		(UNPAID, 'Unpaid'),
		(INVOICED, 'Invoiced'),
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
		if self.status == Reconcile.COMP:
			return 0
		elif not self.custom_rate:
			return self.default_rate()
		else:
			return self.custom_rate
	get_rate.short_description = 'Rate'

	def html_color_status(self):
		if self.status == Reconcile.PAID:
			color_code = "#5fbf00"
		elif self.status == Reconcile.UNPAID or self.status == Reconcile.INVOICED:
			color_code = "#bf0000"
		elif self.status == Reconcile.COMP:
			color_code = "#ffc000"
		else:
			color_code = "#000000"
		return '<span style="color: %s;">%s</span>' % (color_code, self.status)
	html_color_status.allow_tags = True


	def default_rate(self):
		# default_rate always returns the default rate regardless of comps or
		# custom rates.
		return self.reservation.room.default_rate

	def total_value(self):
		# value of the reservation, regardless of what has been paid
		# get_rate checks for comps and custom rates. 
		return self.reservation.total_nights()*self.get_rate()

	def total_owed(self):
		# in case some amoutn has been paid already
		if not self.paid_amount:
			return self.reservation.total_nights()*self.get_rate()
		else:
			return self.reservation.total_nights()*self.get_rate() - self.paid_amount


	def total_owed_in_cents(self):
		return self.total_owed()*100

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
			'total': self.total_owed,
		}) 

		subject = "[Embassy SF] Thanks for Staying with us!" 
		sender = "stay@embassynetwork.com"
		recipients = [self.reservation.user.email,]
		text_content = plaintext.render(c)
		html_content = htmltext.render(c)
		msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		self.status = Reconcile.INVOICED
		self.save()

	def send_receipt(self):
		if self.reservation.hosted:
			# XXX TODO make this a proper error which is viewable in the admin form.
			print "hosted reservation invoices not supported"
			return False
		if not self.status == Reconcile.UNPAID and not self.status == Reconcile.PAID:
			# XXX TODO proper error handling. 
			print "reservation must be unpaid or paid to generate receipt"
			return False

		if (not self.paid_amount or not self.payment_method or not self.transaction_id 
			or not self.payment_date):
			return False

		total_paid = self.paid_amount

		plaintext = get_template('emails/receipt.txt')
		htmltext = get_template('emails/receipt.html')
		c = Context({
			'first_name': self.reservation.user.first_name, 
			'last_name': self.reservation.user.last_name, 
			'res_id': self.reservation.id,
			'today': datetime.datetime.today(), 
			'arrive': self.reservation.arrive, 
			'depart': self.reservation.depart, 
			'room': self.reservation.room.name, 
			'num_nights': self.reservation.total_nights(), 
			'rate': self.get_rate(), 
			'payment_method': self.payment_method,
			'transaction_id': self.transaction_id,
			'payment_date': self.payment_date,
			'total_paid': total_paid,
		}) 

		subject = "[Embassy SF] Receipt for your Stay %s - %s" % (str(self.reservation.arrive), str(self.reservation.depart))  
		sender = "stay@embassynetwork.com"
		recipients = [self.reservation.user.email,]
		text_content = plaintext.render(c)
		html_content = htmltext.render(c)
		msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		if self.status != Reconcile.PAID:
			self.status = Reconcile.PAID
			self.save()
		return True

	def charge_card(self):
		# stripe will raise a stripe.CardError if the charge fails. this
		# function purposefully does not handle that error so the calling
		# function can decide what to do. 
		domain = 'http://' + Site.objects.get_current().domain
		descr = "%s %s from %s - %s. Details: %s." % (self.reservation.user.first_name, 
				self.reservation.user.last_name, str(self.reservation.arrive), 
				str(self.reservation.depart), domain + self.reservation.get_absolute_url())

		amt_owed = self.total_owed_in_cents()
		stripe.api_key = settings.STRIPE_SECRET_KEY
		charge = stripe.Charge.create(
				amount=amt_owed,
				currency="usd",
				customer = self.reservation.user.profile.customer_id,
				description=descr
		)

		# store the charge details
		self.status = Reconcile.PAID
		self.payment_service = "Stripe"
		self.payment_method = charge.card.type
		self.paid_amount = (charge.amount/100)
		self.transaction_id = charge.id
		self.payment_date = datetime.datetime.now()
		self.save()
		self.send_receipt()


Reservation.reconcile = property(lambda r: Reconcile.objects.get_or_create(reservation=r)[0])

def profile_img_upload_to(instance, filename):
	ext = filename.split('.')[-1]
	# rename file to random string
	filename = "%s.%s" % (uuid.uuid4(), ext.lower())

	upload_path = "data/avatars/%s/" % instance.user.username
	upload_abs_path = os.path.join(settings.MEDIA_ROOT, upload_path)
	print upload_path
	print upload_abs_path
	print filename
	print "*****"
	if not os.path.exists(upload_abs_path):
		os.makedirs(upload_abs_path)
	return os.path.join(upload_path, filename)

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
	image = models.ImageField(upload_to=profile_img_upload_to, help_text="Image should have square dimensions.")
	image_thumb = models.ImageField(upload_to="data/avatars/%Y/%m/%d/", blank=True, null=True)
	bio = models.TextField("About you", blank=True, null=True)
	links = models.TextField(help_text="Comma-separated", blank=True, null=True)

	projects = models.TextField(verbose_name='Current Projects', help_text='Describe one or more projects you are currently working on')
	sharing = models.TextField(help_text="Is there anything you'd be interested in learning or sharing during your stay?")
	discussion = models.TextField(help_text="We like discussing thorny issues with each other. What's a question that's been on your mind lately that you don't know the answer to?")
	referral = models.CharField(max_length=200, verbose_name='How did you hear about us?')
	# currently used to store the stripe customer id but could be used for
	# other payment platforms in the future
	customer_id = models.CharField(max_length=200, blank=True, null=True)

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
		img_upload_path_rel = profile_img_upload_to(instance, instance.image.name)
		print img_upload_path_rel
		main_img_full_path = os.path.join(settings.MEDIA_ROOT, img_upload_path_rel)
		# resize returns a copy. resize() forces the dimensions of the image
		# to match SIZE specified, squeezing the image if necessary along one
		# dimension.
		main_img = im.resize(UserProfile.IMG_SIZE, Image.ANTIALIAS)
		main_img.save(main_img_full_path)
        # the image field is a link to the path where the image is stored
		instance.image = img_upload_path_rel
		# now resize this to generate the smaller thumbnail
		thumb_img = im.resize(UserProfile.IMG_THUMB_SIZE, Image.ANTIALIAS)
		thumb_full_path = os.path.splitext(main_img_full_path)[0] + ".thumb" + os.path.splitext(main_img_full_path)[1]
		thumb_img.save(thumb_full_path)
		# the ImageFileField needs the path info relative to the media
		# directory
		# XXX Q: does this save the file twice? once by PIL and another time
		# reading it in and saving it to the same place when the model saves?
		thumb_rel_path = os.path.join(os.path.split(img_upload_path_rel)[0], os.path.basename(thumb_full_path))
		instance.image_thumb = thumb_rel_path
		print thumb_rel_path	

		# now delete any old images
		if obj and obj.image and obj.image.name != "data/avatars/default.jpg":
			default_storage.delete(obj.image.path)

		if obj and obj.image_thumb and obj.image_thumb.name != "data/avatars/default.thumb.jpg":
			default_storage.delete(obj.image_thumb.path)


		

