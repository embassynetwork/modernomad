from graphene import relay, ObjectType
from graphene.contrib.django.filter import DjangoFilterConnectionField
from graphene.contrib.django.types import DjangoNode
from graphene.utils import with_context

from core.models import Reservation, Location


class ReservationNode(DjangoNode):
    class Meta:
        model = Reservation
        filter_fields = ['arrive', 'location']
        filter_order_by = True


class Query(ObjectType):
    my_reservations = DjangoFilterConnectionField(ReservationNode)

    class Meta:
        abstract = True

    @with_context
    def resolve_my_reservations(self, args, context, info):
        if not context.user.is_authenticated():
            return Reservation.objects.none()
        else:
            return Reservation.objects.filter(user=context.user)
