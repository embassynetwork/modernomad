from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import House, Resource, UserProfile, Reservation

class ReservationAdmin(admin.ModelAdmin):
	model = Reservation
	list_filter = ('status',)
	list_display = ('id', 'user', 'status', 'arrive', 'depart')

class ResourceInline(admin.TabularInline):
    model = Resource

class HouseAdmin(admin.ModelAdmin):
    inlines = [ResourceInline]

class UserProfileInline(admin.StackedInline):
    model = UserProfile
 
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]


admin.site.register(House, HouseAdmin) 
admin.site.register(Reservation, ReservationAdmin)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
