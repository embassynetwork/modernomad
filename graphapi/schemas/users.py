from graphene import relay, ObjectType
import graphene
from graphene.contrib.django.filter import DjangoFilterConnectionField
from graphene.contrib.django.types import DjangoNode
from graphene.utils import with_context

from django.contrib.auth.models import User


class UserNode(DjangoNode):
    class Meta:
        model = User
        only_fields = ['username', 'first_name', 'last_name', 'email']


class Query(ObjectType):
    # current_user = DjangoFilterConnectionField(UserNode)
    current_user = graphene.Field(UserNode)

    class Meta:
        abstract = True

    @with_context
    def resolve_current_user(self, args, context, info):
        return context.user if context.user else None
