import graphene

import graphapi.schemas.reservations
import graphapi.schemas.locations
import graphapi.schemas.users
import graphapi.schemas.resources


class Query(
    graphapi.schemas.reservations.Query,
    graphapi.schemas.locations.Query,
    graphapi.schemas.users.Query,
    graphapi.schemas.resources.Query,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(query=Query)
