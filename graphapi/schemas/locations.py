from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Location


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        interfaces = (Node, )


class Query(AbstractType):
    all_locations = DjangoFilterConnectionField(LocationNode)
