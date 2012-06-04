from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import Endorsement, House, Resource, UserProfile


class UserProfileInline(admin.StackedInline):
	model = UserProfile
 
class UserProfileAdmin(UserAdmin):
	inlines = [UserProfileInline]
 

admin.site.register(House)
admin.site.register(Resource)
admin.site.register(Endorsement)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
