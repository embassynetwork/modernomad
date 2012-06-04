from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration import signals
import registration.backends.default
from registration.models import RegistrationProfile

from core.models import UserProfile


def ListUsers(request):
    return HttpResponse("Show all users")

def ListLocations(request):
    return render_to_response("locations.html")

def GetUser(request, user_id):
   return HttpResponse("This is a specific user page")


class RegistrationBackend(registration.backends.default.DefaultBackend):
    '''A registration backend that supports capturing user profile
    information during registration.'''
    
    @transaction.commit_on_success
    def register(self, request, **cleaned_data):
        '''Register a new user, saving the User and UserProfile data.'''
        # We can't use RegistrationManager.create_inactive_user()
        # because it doesn't play nice with saving other information
        # in the same transaction.
        user = User(is_active=False)
        for field in user._meta.fields:
            if field.name in cleaned_data:
                setattr(user, field.name, cleaned_data[field.name])
        user.save()

        profile = UserProfile(user=user)
        for field in profile._meta.fields:
            if field.name in cleaned_data:
                setattr(profile, field.name, cleaned_data[field.name])
        profile.save()

        registration_profile = RegistrationProfile.objects.create_profile(user)
        registration_profile.send_activation_email(Site.objects.get_current())

        signals.user_registered.send(sender=self.__class__, user=user, request=request)
