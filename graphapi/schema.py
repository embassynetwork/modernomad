import graphene

import graphapi.schemas.events
import graphapi.schemas.reservations
import graphapi.schemas.locations


class Query(
    graphapi.schemas.events.Query,
    graphapi.schemas.reservations.Query,
    graphapi.schemas.locations.Query
):
    pass

schema = graphene.Schema(name='Modernomad Schema')
schema.query = Query
