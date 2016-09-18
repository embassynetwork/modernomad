from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.contrib.auth.models import User


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (Node, )


class Query(AbstractType):
    all_users = DjangoFilterConnectionField(UserNode)
