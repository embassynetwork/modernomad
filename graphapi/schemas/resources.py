import graphene
from graphene import AbstractType, Field, Node
from graphene.types.datetime import *
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import time
from core.models import Resource


class AvailabilityNode(graphene.ObjectType):
    date = DateTime()
    quantity = graphene.Int()


class ResourceNode(DjangoObjectType):
    rid = graphene.Int()
    availabilities = graphene.List(lambda: AvailabilityNode, arrive=DateTime(), depart=DateTime())

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

        time.sleep(1)

        availabilities = self.daily_availabilities_within(args['arrive'].date(), args['depart'].date())

        return [AvailabilityNode(*availability) for availability in availabilities]


class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
