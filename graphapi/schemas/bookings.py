import graphene
from graphene import AbstractType, Field, Node, relay
from graphene_django.types import DjangoObjectType
from graphene.types import String
from graphene_django.filter import DjangoFilterConnectionField
from graphene.types.datetime import *

# from core.models import Booking
# from core.forms import BookingUseForm
from api.commands.bookings import RequestBooking

class RequestBookingMutation(graphene.Mutation):
    class Input:
        arrive = DateTime(required=True)
        depart = DateTime(required=True)

    name = graphene.String()

    @classmethod
    def mutate(cls, root, data, context, info):
        # form = BookingUseForm(None, args)
        # if form.is_valid():
        #     return CreateBooking(name=str(valid))
        # else:
        command = RequestBooking(context.user, **data)
        command.execute()
        return RequestBookingMutation(name=str(command.result()))
