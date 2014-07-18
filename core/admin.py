from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import *
from gather.models import EventAdminGroup
from core.emails import send_invoice, send_receipt

class EmailTemplateAdmin(admin.ModelAdmin):
	model = EmailTemplate
	exclude = ('creator',)
	def save_model(self, request, obj, form, change): 
		obj.creator = request.user 
		obj.save() 

class EventAdminGroupInline(admin.TabularInline):
	model = EventAdminGroup
	filter_horizontal = ['users',]

class RoomAdminInline(admin.TabularInline):
	model = Room
	extra = 0

class LocationAdmin(admin.ModelAdmin):
	model=Location
	list_display=('name', 'address')
	list_filter=('name',)
	filter_horizontal = ['residents', 'house_admins']
	inlines = [RoomAdminInline, EventAdminGroupInline]

class PaymentAdmin(admin.ModelAdmin):
	def user(self):
		return '''<a href="/people/%s">%s %s</a> (%s)''' % (self.reservation.user.username, self.reservation.user.first_name, self.reservation.user.last_name, self.reservation.user.username)
	user.allow_tags = True

	def reservation(self):
		return '''<a href="/locations/%s/reservation/%s/">%s''' % (self.reservation.location.slug, self.reservation.id, self.reservation)
	reservation.allow_tags = True

	model=Payment
	list_display=('payment_date', user,  reservation, 'payment_method', 'paid_amount')
	list_filter = ('payment_method',)
	ordering = ['-payment_date',]

class PaymentInline(admin.TabularInline):
	model = Payment
	extra = 0

class BillLineItemAdmin(admin.ModelAdmin):
	def user(self):
		return '''<a href="/people/%s">%s %s</a> (%s)''' % (self.reservation.user.username, self.reservation.user.first_name, self.reservation.user.last_name, self.reservation.user.username)
	user.allow_tags = True

	def location(self):
		return self.reservation.location

	list_display = ('id', 'reservation', user, location, 'description', 'amount', 'paid_by_house')

class BillLineItemInline(admin.TabularInline):
	model = BillLineItem
	fields = ('fee', 'description', 'amount', 'paid_by_house')
	readonly_fields = ('fee',)
	extra = 0

class ReservationAdmin(admin.ModelAdmin):
	def rate(self):
		return "$%d" % self.rate

	def value(self):
		return "$%d" % self.total_value()

	def bill(self):
		return "$%d" % self.bill_amount()

	def fees(self):
		return "$%d" % self.non_house_fees()

	def to_house(self):
		return "$%d" % self.to_house()
		
	def paid(self):
		return "$%d" % self.total_paid()

	def user_profile(self):
		return '''<a href="/people/%s">%s %s</a> (%s)''' % (self.user.username, self.user.first_name, self.user.last_name, self.user.username)
	user_profile.allow_tags = True

	def send_invoice(self, request, queryset):
		for res in queryset:
			send_invoice(res)
		if len(queryset) == 1:
			prefix = "1 invoice was"
		else:
			prefix = "%d invoices were" % len(queryset)
		msg = prefix + " sent"
		self.message_user(request, msg)

	def send_receipt(self, request, queryset):
		success_list = []
		failure_list = []
		for res in queryset:
			if send_receipt(res):
				success_list.append(str(res.id))
			else:
				failure_list.append(str(res.id))
		msg = ""
		if len(success_list) > 0:
			msg += "Receipts sent for reservation(s) %s. " % ",".join(success_list)
		if len(failure_list) > 0:
			msg += "Receipt sending failed for reservation(s) %s. (Make sure all payment information has been entered in the reservation details and that the status of the reservation is either unpaid or paid.)" % ",".join(failure_list)
		self.message_user(request, msg)

	def mark_as_comp(self, request, queryset):
		for res in queryset:
			res.comp()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " marked as comp."
		self.message_user(request, msg)

	def reset_rate(self, request, queryset):
		for res in queryset:
			res.reset_rate()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " set to default rate."
		self.message_user(request, msg)

	def generate_bill(self, request, queryset):
		for res in queryset:
			res.generate_bill()
		if len(queryset) == 1:
			prefix = "1 bill was"
		else:
			prefix = "%d bills were" % len(queryset)
		msg = prefix + " generated."
		self.message_user(request, msg)

	model = Reservation
	list_filter = ('status', 'hosted')
	list_display = ('id', user_profile, 'status', 'arrive', 'depart', 'room', 'hosted', 'total_nights', rate, fees, bill, to_house, paid )
	list_editable = ('status',)
	inlines = [BillLineItemInline, PaymentInline]
	ordering = ['depart',]
	actions= ['send_invoice', 'send_receipt', 'generate_bill', 'mark_as_comp', 'reset_rate']
	save_as = True
	
class UserProfileInline(admin.StackedInline):
	model = UserProfile
 
class UserProfileAdmin(UserAdmin):
	inlines = [UserProfileInline]
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login')

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(BillLineItem, BillLineItemAdmin)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)

admin.site.register(Fee)
admin.site.register(LocationFee)
