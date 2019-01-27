import graphene
from graphene import AbstractType, Field, Node
from graphene_django.types import DjangoObjectType
from gather.models import Event
from graphene_django.filter import DjangoFilterConnectionField


class EventNode(DjangoObjectType):
    url = graphene.String()

    class Meta:
        model = Event
        filter_fields = ['slug', 'title']

    def resolve_url(self, info, **kwargs):
        return "/locations/" + self.location.slug + "/events/" + str(self.id) + "/" + self.slug + "/"


class Query(AbstractType):
    # event = relay.NodeField(EventNode)
    all_events = DjangoFilterConnectionField(EventNode)
