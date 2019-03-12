import graphene
from graphene import AbstractType, Field, Node, relay
from graphene_django.types import DjangoObjectType
from graphene.types import String
from graphene_django.filter import DjangoFilterConnectionField
from graphene.types.datetime import *

from api.commands.bookings import RequestBooking
from graphapi.schemas.resources import ResourceNode
from modernomad.core.models import Resource, Booking


def commandErrorsToGraphQL(errors):
    result = []
    for field_name, messages in errors.iteritems():
        for message in messages:
            result.append([field_name, message])
    return result


class BookingNode(DjangoObjectType):
    class Meta:
        model = Booking
        interfaces = (Node, )


class RequestBookingMutation(graphene.Mutation):
    class Input:
        arrive = DateTime(required=True)
        depart = DateTime(required=True)
        resource = graphene.String(required=True)
        purpose = graphene.String(required=False)
        arrival_time = graphene.String(required=False)
        comments = graphene.String(required=False)

    booking = graphene.Field(BookingNode)
    errors = graphene.List(graphene.List(graphene.String))
    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, data, context, info):
        command = RequestBooking(context.user, **data)
        if command.execute():
            return RequestBookingMutation(ok=True, booking=command.result().data.get('booking'))
        else:
            return RequestBookingMutation(ok=False, errors=commandErrorsToGraphQL(command.result().errors))
