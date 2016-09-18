import graphene

import graphapi.schemas.events
import graphapi.schemas.reservations
import graphapi.schemas.locations
import graphapi.schemas.users


class Query(
    graphapi.schemas.events.Query,
    graphapi.schemas.reservations.Query,
    graphapi.schemas.locations.Query,
    graphapi.schemas.users.Query
):
    pass

schema = graphene.Schema(name='Modernomad Schema')
schema.query = Query
