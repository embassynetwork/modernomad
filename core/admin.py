from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import UserProfile, Reservation, Reconcile, Room

class RoomAdmin(admin.ModelAdmin):
	model = Room
	list_display = ('name', 'default_rate', 'primary_use')
	list_filter = ('primary_use',)

class ReconcileInline(admin.TabularInline):
	model = Reconcile

def reconcile_status(obj):
	return obj.reconcile.status

def current_rate(obj):
	return obj.reconcile.get_rate()

def automatic_invoice(obj):
	return obj.reconcile.automatic_invoice

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
	list_display = ('__unicode__', 'user', 'status', 'arrive', 'depart', 'total_nights', 'room', 'hosted', paid_status, current_rate, automatic_invoice)
	inlines = [ReconcileInline]
	ordering = ['depart',]
	actions= ['send_invoice', 'reconcile_as_paid', 'reconcile_as_unpaid', 'reconcile_as_comp', 'reconcile_as_invalid', 'reconcile_as_invoiced']
	
class UserProfileInline(admin.StackedInline):
    model = UserProfile
 
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login')


admin.site.register(Reservation, ReservationAdmin)
#admin.site.register(Reconcile, ReconcileAdmin)
admin.site.register(Room, RoomAdmin)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
