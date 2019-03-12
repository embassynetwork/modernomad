from django.contrib import messages
from django.http import HttpResponseRedirect

from modernomad.core.models import *
from django.contrib.auth.models import User


def _get_user_and_perms(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        messages.add_message(request, messages.INFO, 'There is no user with that username.')
        return HttpResponseRedirect('/404')

    user_is_house_admin_somewhere = False
    for location in Location.objects.filter(visibility='public'):
        if request.user in location.house_admins.all():
            user_is_house_admin_somewhere = True
            break
    return user, user_is_house_admin_somewhere
