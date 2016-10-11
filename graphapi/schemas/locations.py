from graphene import AbstractType, Field, Node, List
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Location
from .resources import ResourceNode

class LocationNode(DjangoObjectType):
    # resources = List(lambda: ResourceNode)

    class Meta:
        model = Location
        interfaces = (Node, )
        filter_fields = ['slug']


class Query(AbstractType):
    all_locations = DjangoFilterConnectionField(LocationNode)
