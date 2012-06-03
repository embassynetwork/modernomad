from wc_profiles.models import House
from wc_profiles.models import Resource
from wc_profiles.models import Endorsement
from django.contrib import admin

admin.site.register(House)
admin.site.register(Resource)
admin.site.register(Endorsement)

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from wc_profiles.models import UserProfile
 
admin.site.unregister(User)
 
class UserProfileInline(admin.StackedInline):
	model = UserProfile
 
class UserProfileAdmin(UserAdmin):
	inlines = [UserProfileInline]
 
admin.site.register(User, UserProfileAdmin)
