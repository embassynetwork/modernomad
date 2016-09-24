import graphene

import graphapi.schemas.occupants
import graphapi.schemas.locations
import graphapi.schemas.users


class Query(
    graphapi.schemas.occupants.Query,
    graphapi.schemas.locations.Query,
    graphapi.schemas.users.Query,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(query=Query)
