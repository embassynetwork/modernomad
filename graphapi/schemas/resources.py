import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Resource


class ResourceNode(DjangoObjectType):
    rid = graphene.Int()

    class Meta:
        model = Resource
        interfaces = (Node, )
        filter_fields = {
            'location': ['exact'],
            'location__slug': ['exact'],
        }
        # filter_order_by = ['slug']

    def resolve_rid(self, args, *_):
        return self.id


class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
