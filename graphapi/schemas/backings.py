import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Backing

class BackingNode(DjangoObjectType):
    resource_id = graphene.Int()

    class Meta:
        model = Backing
        interfaces = (Node, )
        filter_fields = ['resource_id']


class Query(AbstractType):
    all_backings = DjangoFilterConnectionField(BackingNode)
