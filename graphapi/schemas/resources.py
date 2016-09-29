import graphene
from graphene import AbstractType, Field, Node
from graphene.types.datetime import *
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Resource


class UsabilityNode(graphene.ObjectType):
    date = DateTime()
    quantity = graphene.Int()


class ResourceNode(DjangoObjectType):
    rid = graphene.Int()
    usabilities = graphene.List(lambda: UsabilityNode, arrive=DateTime(), depart=DateTime())

    class Meta:
        model = Resource
        interfaces = (Node, )
        filter_fields = {
            'location': ['exact'],
            'location__slug': ['exact'],
        }

    def resolve_rid(self, args, *_):
        return self.id

    def resolve_usabilities(self, args, *stuff):
        return [UsabilityNode(args['arrive'], 12)]


class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
