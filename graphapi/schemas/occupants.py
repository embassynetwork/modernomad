import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene.types import String
from graphene_django.filter import DjangoFilterConnectionField
from .users import UserNode
from core.models import Booking, Location
from django.contrib.auth.models import User


class OccupantNode(DjangoObjectType):
    occupants_during = graphene.List(lambda: OccupantNode)
    type = graphene.String()

    class Meta:
        model = Booking
        interfaces = (Node, )
        filter_fields = ['arrive', 'location']
        filter_order_by = True

    def resolve_occupants_during(self, args, *_):
        return Booking.objects.all()[:15]

    def resolve_type(self, args, *_):
        return "guest"


class Query(AbstractType):
    my_occupancies = DjangoFilterConnectionField(OccupantNode)

    def resolve_my_occupancies(self, args, context, info):
        if not context.user.is_authenticated():
            return Booking.objects.none()
        else:
            return Booking.objects.filter(user=context.user)
