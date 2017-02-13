import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene.types.datetime import *

from core.models import Backing
from core.models import Resource
from django.contrib.auth.models import User

from graphapi.schemas.users import UserNode

class BackingNode(DjangoObjectType):
    resource_id = graphene.Int()
    backers = graphene.List(graphene.Int)
    start = DateTime()

    class Meta:
        model = Backing
        interfaces = (Node, )
        filter_fields = ['resource_id']


class Query(AbstractType):
    all_backings = DjangoFilterConnectionField(BackingNode)

class BackingMutation(graphene.Mutation):
    class Input:
        resource = graphene.Int()
        backers = graphene.List(graphene.Int)
        start = DateTime(required=True)

    backing = graphene.Field(BackingNode)
    errors = graphene.List(graphene.List(graphene.String))
    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, data, context, info):
        id = data['resource']
        resource = Resource.objects.get(pk=id)
        backers = [User.objects.get(pk=i) for i in data['backers']]
        start = data['start'].date()
        new_backing = resource.set_next_backing(backers, start)
        if new_backing:
            return BackingMutation(ok=True, backing=new_backing)
