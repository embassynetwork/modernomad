import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene.types import String
from graphene_django.filter import DjangoFilterConnectionField
from core.models import Use, Location
from django.contrib.auth.models import User
from django.utils import timezone

from .users import UserNode
from .events import EventNode
from gather.models import Event


class OccupantNode(DjangoObjectType):
    occupants_during = graphene.List(lambda: OccupantNode)
    upcoming_events_during = graphene.List(lambda: EventNode)
    type = graphene.String()

    class Meta:
        model = Use
        interfaces = (Node, )
        filter_fields = ['arrive', 'location']
        filter_order_by = True

    def resolve_occupants_during(self, args, *_):
        query = (
            Use.objects
            .filter(location=self.location, status="confirmed")
            .exclude(user=self.user)
            .filter(arrive__lte=self.depart)
            .filter(depart__gte=self.arrive)
            .order_by('user__last_name', 'user__first_name')
            .distinct('user__last_name', 'user__first_name')
        )
        return query.all()

    def resolve_upcoming_events_during(self, args, *_):
        today = timezone.now()

        query = (
            Event.objects
            .filter(location=self.location, status="live", visibility="public")
            .filter(start__lte=self.depart)
            .filter(end__gte=self.arrive)
            .filter(start__gte=today)
            .order_by('start')
        )
        return query.all()[:3]

    def resolve_type(self, args, *_):
        return "guest"


class Query(AbstractType):
    my_occupancies = DjangoFilterConnectionField(OccupantNode)
    my_current_occupancies = DjangoFilterConnectionField(OccupantNode)

    def resolve_my_occupancies(self, args, context, info):
        if not context.user.is_authenticated():
            return Use.objects.none()
        else:
            return Use.objects.filter(user=context.user)

    def resolve_my_current_occupancies(self, args, context, info):
        if not context.user.is_authenticated():
            return Use.objects.none()
        else:
            today = timezone.now()
            return Use.objects.filter(user=context.user, depart__gte=today)
