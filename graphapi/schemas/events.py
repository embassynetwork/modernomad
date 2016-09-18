from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from gather.models import Event
from graphene_django.filter import DjangoFilterConnectionField

class EventNode(DjangoObjectType):
    class Meta:
        model = Event
        filter_fields = ['slug', 'title']
        filter_order_by = ['slug']


class Query(AbstractType):
    # event = relay.NodeField(EventNode)
    all_events = DjangoFilterConnectionField(EventNode)
