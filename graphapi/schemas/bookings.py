import graphene
from graphene import AbstractType, Field, Node, relay
from graphene_django.types import DjangoObjectType
from graphene.types import String
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Booking


class CreateBooking(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    name = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        return CreateBooking()
