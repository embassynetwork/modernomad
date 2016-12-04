import graphene
from graphene import AbstractType, Field, Node
from graphene.types.datetime import *
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from datetime import timedelta
from core.models import Resource, Backing


class AvailabilityNode(graphene.ObjectType):
    date = DateTime()
    quantity = graphene.Int()

class BackingNode(DjangoObjectType):
    class Meta:
        model = Backing
        interfaces = (Node, )

class ResourceNode(DjangoObjectType):
    rid = graphene.Int()
    availabilities = graphene.List(lambda: AvailabilityNode, arrive=DateTime(), depart=DateTime())
    backing = graphene.Field(BackingNode)
    
    class Meta:
        model = Resource
        interfaces = (Node, )
        filter_fields = {
            'location': ['exact'],
            'location__slug': ['exact'],
        }

    def resolve_rid(self, args, *_):
        return self.id

    def resolve_availabilities(self, args, *stuff):
        assert args['arrive'], "you must specify arrival date"
        assert args['depart'], "you must specify departure date"

        start_date = args['arrive'].date()
        end_date = args['depart'].date() - timedelta(days=1)

        availabilities = self.daily_availabilities_within(start_date, end_date)

        return [AvailabilityNode(*availability) for availability in availabilities]

class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
