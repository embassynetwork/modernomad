import graphene

import graphapi.schemas.occupants
import graphapi.schemas.locations
import graphapi.schemas.users
import graphapi.schemas.resources
import graphapi.schemas.bookings


class Query(
    graphapi.schemas.occupants.Query,
    graphapi.schemas.locations.Query,
    graphapi.schemas.users.Query,
    graphapi.schemas.resources.Query,
    graphene.ObjectType
):
    pass


class Mutation(graphene.ObjectType):
    create_booking = graphapi.schemas.bookings.CreateBooking.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
