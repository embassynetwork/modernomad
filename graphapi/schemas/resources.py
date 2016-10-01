import graphene
from graphene import AbstractType, Field, Node
from graphene.types.datetime import *
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Resource


class BookabilityNode(graphene.ObjectType):
    date = DateTime()
    quantity = graphene.Int()


class ResourceNode(DjangoObjectType):
    rid = graphene.Int()
    bookabilities = graphene.List(lambda: BookabilityNode, arrive=DateTime(), depart=DateTime())

    class Meta:
        model = Resource
        interfaces = (Node, )
        filter_fields = {
            'location': ['exact'],
            'location__slug': ['exact'],
        }

    def resolve_rid(self, args, *_):
        return self.id

    def resolve_bookabilities(self, args, *stuff):
        assert args['arrive'], "you must specify arrival date"
        assert args['depart'], "you must specify departure date"

        bookabilities = self.daily_bookabilities_within(args['arrive'].date(), args['depart'].date())

        return [BookabilityNode(*bookability) for bookability in bookabilities]


class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
