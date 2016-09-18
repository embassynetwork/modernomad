from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Reservation, Location


class ReservationNode(DjangoObjectType):
    class Meta:
        model = Reservation
        interfaces = (Node, )
        filter_fields = ['arrive', 'location']
        filter_order_by = True


class Query(AbstractType):
    my_reservations = DjangoFilterConnectionField(ReservationNode)

    def resolve_my_reservations(self, args, context, info):
        if not context.user.is_authenticated():
            return Reservation.objects.none()
        else:
            return Reservation.objects.filter(user=context.user)
