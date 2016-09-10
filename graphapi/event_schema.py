from graphene import relay, ObjectType
from graphene.contrib.django.filter import DjangoFilterConnectionField
from graphene.contrib.django.types import DjangoNode

from gather.models import Event


class EventNode(DjangoNode):
    class Meta:
        model = Event
        filter_fields = ['slug', 'title']
        filter_order_by = ['slug']


class Query(ObjectType):
    event = relay.NodeField(EventNode)
    all_events = DjangoFilterConnectionField(EventNode)

    class Meta:
        abstract = True
