import graphene
from graphene import relay, AbstractType, Field, Node
from graphene.types.datetime import *
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from datetime import timedelta
from core.models import Resource, Backing
from graphapi.schemas.backings import BackingNode
from graphapi.schemas.users import UserNode

class AvailabilityNode(graphene.ObjectType):
    date = DateTime()
    quantity = graphene.Int()

class ResourceNode(DjangoObjectType):
    rid = graphene.Int()
    availabilities = graphene.List(lambda: AvailabilityNode, arrive=DateTime(), depart=DateTime())
    backing = graphene.Field(BackingNode)
    has_future_drft_capacity = graphene.Boolean()
    accept_drft_these_dates = graphene.Boolean(arrive=DateTime(), depart=DateTime())
    scheduled_future_backings = graphene.List(lambda: BackingNode)
    current_backers = graphene.List(lambda: UserNode)

    class Meta:
        model = Resource
        interfaces = (relay.Node, )
        filter_fields = {
            'id': ['exact'],
            'location': ['exact'],
            'location__slug': ['exact'],
        }

    def resolve_has_future_drft_capacity(self, args, *kwargs):
        return self.has_future_drft_capacity()

    def resolve_rid(self, args, *_):
        return self.id

    def resolve_accept_drft_these_dates(self, args, *stuff):
        assert args['arrive'], "you must specify arrival date"
        assert args['depart'], "you must specify departure date"

        start_date = args['arrive'].date()
        end_date = args['depart'].date() - timedelta(days=1)

        print '%s drftable between? ' % self.name
        print self.drftable_between(start_date, end_date)
        return self.drftable_between(start_date, end_date)

    def resolve_availabilities(self, args, *stuff):
        assert args['arrive'], "you must specify arrival date"
        assert args['depart'], "you must specify departure date"

        start_date = args['arrive'].date()
        end_date = args['depart'].date() - timedelta(days=1)

        availabilities = self.daily_availabilities_within(start_date, end_date)

        return [AvailabilityNode(*availability) for availability in availabilities]

    def resolve_scheduled_future_backings(self, *args, **kwargs):
        return self.scheduled_future_backings()

    def resolve_current_backers(self, *args, **kwargs):
        return self.current_backers()


class Query(AbstractType):
    all_resources = DjangoFilterConnectionField(ResourceNode)
    all_drft_resources = DjangoFilterConnectionField(ResourceNode)
    resource = graphene.Field(ResourceNode, id=graphene.ID(), description="single resource") 

    def resolve_all_drft_resources(self, args, context, info):
        return Resource.objects.filter(hasFutureDrftCapacity=True)

    def resolve_resource(self, args, context, info):
        id = args.get('id')
        return Resource.objects.get(pk=id)




