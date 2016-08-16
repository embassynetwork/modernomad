from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from jwt_auth.mixins import JSONWebTokenAuthMixin
from django.views.generic import View

from api.utils.http import JSONResponse
from api.commands.availabilities import *

from core.models import Availability


class CurrentLocationOccupancies(JSONWebTokenAuthMixin, View):
    ''' Expects a proper JWT token to be passed into the header. If valid, the
    user will be treated as logged in. If not, the method will return 401
    unauthorized.'''

    def where(self, user):
        ''' tell us where the user is today. this method is necessarily...
        opinionated. it treats guest bookings >> residence >> membership.'''

        today = timezone.now()
        reservations = Reservation.objects.filter(user=user, depart__gte=today, arrive__lte=today)
        residences = user.residences.all()
        subscriptions = Subscription.objects.active_subscriptions().filter(user=user)

        user_location = None
        if reservations:
            # take the first one...
            user_location = reservations[0].location

        elif residences:
            # just take the first one...
            user_location = residences[0]

        elif subscriptions:
            # just take the first one...
            user_location = subscriptions[0].location

        return user_location

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponse(status=404)

        location = self.where(user)
        print 'location'
        print location
        data = {}

        if location:
            # people today includes residents, guests and subscribers. does not
            # currently include event attendees.
            people_today = location.people_today()
            print 'people today'
            print people_today

            data['location'] = {'id': location.id, 'name': location.name}
            occupants = []
            domain = "https://" + Site.objects.get_current().domain
            for u in people_today:
                try:
                    profile_img = domain + u.profile.image.url
                except:
                    profile_img = None

                user_data = {
                        'id': u.id,
                        'name': "%s %s" % (u.first_name, u.last_name),
                        'username': u.username,
                        'avatar': profile_img,
                        'profile_url': domain + reverse('user_detail', args=(u.username,)),
                    }
                occupants.append(user_data)
            data['location']['occupants'] = occupants

        json_data = json.dumps(data)
        return HttpResponse(json_data)
