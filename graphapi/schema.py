import graphene

import graphapi.event_schema


class Query(graphapi.event_schema.Query):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(name='Modernomad Schema')
schema.query = Query
