import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene.types import String
from graphene_django.filter import DjangoFilterConnectionField
from .users import UserNode
from core.models import Reservation, Location
from django.contrib.auth.models import User


class ReservationNode(DjangoObjectType):
    occupants = graphene.List(lambda: UserNode)

    class Meta:
        model = Reservation
        interfaces = (Node, )
        filter_fields = ['arrive', 'location']
        filter_order_by = True

    def resolve_occupants(self, args, *_):
        return User.objects.all()[:15]


class Query(AbstractType):
    my_reservations = DjangoFilterConnectionField(ReservationNode)

    def resolve_my_reservations(self, args, context, info):
        if not context.user.is_authenticated():
            return Reservation.objects.none()
        else:
            return Reservation.objects.filter(user=context.user)
