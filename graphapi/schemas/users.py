import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.contrib.auth.models import User
from core.models import UserProfile
from bank.models import Account, Currency


class UserProfileNode(DjangoObjectType):
    class Meta:
        model = UserProfile
        interfaces = (Node, )

class AccountNode(DjangoObjectType):
    balance = graphene.Int()
    class Meta:
        model = Account
        interfaces = (Node, )

    def resolve_balance(self, args, *_):
        return self.get_balance()

class CurrencyNode(DjangoObjectType):
    class Meta:
        model = Currency
        interfaces = (Node, )


class UserNode(DjangoObjectType):
    name = graphene.String()
    url = graphene.String()
    account = graphene.Field(AccountNode)
    currency = graphene.Field(CurrencyNode)

    class Meta:
        model = User
        interfaces = (Node, )
        filter_fields = ['id', 'username']

    def resolve_name(self, args, *_):
        return " ".join([self.first_name, self.last_name])

    def resolve_url(self, args, *_):
        return "/people/" + self.username


class Query(AbstractType):
    all_users = DjangoFilterConnectionField(UserNode)
    current_user = DjangoFilterConnectionField(UserNode)

    def resolve_current_user(self, args, context, info):
        if not context.user.is_authenticated():
            return User.objects.none()
        else:
            return User.objects.filter(username=context.user)
