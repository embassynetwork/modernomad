from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Resource


class ResourceNode(DjangoObjectType):
    class Meta:
        model = Resource
        interfaces = (Node, )
        filter_fields = {
            'location': ['exact']
        }
        # filter_order_by = ['slug']


class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
