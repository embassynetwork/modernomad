from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import UserProfile, Reservation, Reconcile, Room, EmailTemplate, Location

class EmailTemplateAdmin(admin.ModelAdmin):
	model = EmailTemplate
	exclude = ('creator',)
	def save_model(self, request, obj, form, change): 
		obj.creator = request.user 
		obj.save() 

class LocationAdmin(admin.ModelAdmin):
	model=Location
	list_display=('name', 'address')
	list_filter=('name',)

class RoomAdmin(admin.ModelAdmin):
	model = Room
	list_display = ('name', 'default_rate', 'primary_use')
	list_filter = ('primary_use',)

class ReconcileInline(admin.TabularInline):
	model = Reconcile

def reconcile_status(obj):
	return obj.reconcile.status

def rate(obj):
	rate = obj.reconcile.get_rate()
	return "$%d" % rate

def automatic_invoice(obj):
	return obj.reconcile.automatic_invoice

def value(obj):
	value = obj.reconcile.get_rate()*obj.total_nights()
	return "$%d" % value

def user_profile(obj):
	return '''<a href="/people/%s">%s %s</a> (%s)''' % (obj.user.username, obj.user.first_name, obj.user.last_name, obj.user.username)
user_profile.allow_tags = True

def paid_status(obj):
	return obj.reconcile.html_color_status()
# allow_tags tells django not to escape the html returned by the
# html_color_status function.
paid_status.allow_tags = True

class ReservationAdmin(admin.ModelAdmin):
	def send_invoice(self, request, queryset):
		for item in queryset:
			item.reconcile.send_invoice()
		if len(queryset) == 1:
			prefix = "1 invoice was"
		else:
			prefix = "%d invoices were" % len(queryset)
		msg = prefix + " sent"
		self.message_user(request, msg)

	def send_receipt(self, request, queryset):
		success_list = []
		failure_list = []
		for item in queryset:
			if item.reconcile.send_receipt():
				success_list.append(str(item.id))
			else:
				failure_list.append(str(item.id))
		msg = ""
		if len(success_list) > 0:
			msg += "Receipts sent for reservation(s) %s. " % ",".join(success_list)
		if len(failure_list) > 0:
			msg += "Receipt sending failed for reservation(s) %s. (Make sure all payment information has been entered in the reservation details and that the status of the reservation is either unpaid or paid.)" % ",".join(failure_list)
		self.message_user(request, msg)

	def reconcile_as_paid(self, request, queryset):
		for item in queryset:
			rec = item.reconcile
			rec.status = Reconcile.PAID
			rec.save()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " marked as paid."
		self.message_user(request, msg)

	def reconcile_as_unpaid(self, request, queryset):
		for item in queryset:
			rec = item.reconcile
			rec.status = Reconcile.UNPAID
			rec.save()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " marked as unpaid."
		self.message_user(request, msg)

	def reconcile_as_comp(self, request, queryset):
		for item in queryset:
			rec = item.reconcile
			rec.status = Reconcile.COMP
			rec.save()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " marked as comp."
		self.message_user(request, msg)

	def reconcile_as_invalid(self, request, queryset):
		for item in queryset:
			rec = item.reconcile
			rec.status = Reconcile.INVALID
			rec.save()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " marked as invalid."
		self.message_user(request, msg)

	def reconcile_as_invoiced(self, request, queryset):
		for item in queryset:
			rec = item.reconcile
			rec.status = Reconcile.INVOICED
			rec.save()
		if len(queryset) == 1:
			prefix = "1 reservation was"
		else:
			prefix = "%d reservations were" % len(queryset)
		msg = prefix + " marked as invoiced."
		self.message_user(request, msg)


	model = Reservation
	list_filter = ('status','hosted', 'reconcile__status')
	list_display = ('__unicode__', user_profile, 'status', 'arrive', 'depart', 'room', 'hosted', 'total_nights', rate, value, paid_status )
	list_editable = ('status',)
	inlines = [ReconcileInline]
	ordering = ['depart',]
	actions= ['send_invoice', 'send_receipt', 'reconcile_as_paid', 'reconcile_as_unpaid', 'reconcile_as_comp', 'reconcile_as_invalid', 'reconcile_as_invoiced']
	save_as = True
	
class UserProfileInline(admin.StackedInline):
    model = UserProfile
 
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login')


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
