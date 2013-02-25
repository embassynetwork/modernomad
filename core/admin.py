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

	model = Reservation
	list_filter = ('status','hosted', 'reconcile__status')
	list_display = ('__unicode__', 'user', 'status', 'arrive', 'depart', 'room', 'hosted', reconcile_status, current_rate, automatic_invoice)
	inlines = [ReconcileInline]
	actions= ['send_invoice']

# class ReconcileAdmin(admin.ModelAdmin):
# 	def send_invoice(self, request, queryset):
# 		for item in queryset:
# 			item.send_invoice()
# 		if len(queryset) == 1:
# 			prefix = "1 invoice was"
# 		else:
# 			prefix = "%d invoices were" % len(queryset)
# 		msg = prefix + " sent"
# 		self.message_user(request, msg)

# 	model = Reconcile
# 	list_filter = ('status',)
# 	list_display = ('reservation', guest, 'status', room, 'automatic_invoice', 'get_rate', arrive, depart)
# 	actions= ['send_invoice']
	
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
