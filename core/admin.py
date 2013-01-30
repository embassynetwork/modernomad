from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import Resource, UserProfile, Reservation

class ReservationAdmin(admin.ModelAdmin):
	model = Reservation
	list_filter = ('status','hosted')
	list_display = ('__unicode__', 'user', 'created', 'updated', 'status', 'arrive', 'depart', 'hosted')

class ResourceInline(admin.TabularInline):
    model = Resource

class UserProfileInline(admin.StackedInline):
    model = UserProfile
 
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login')


admin.site.register(Reservation, ReservationAdmin)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
