from graphene import relay, ObjectType
from graphene.contrib.django.filter import DjangoFilterConnectionField
from graphene.contrib.django.types import DjangoNode
from graphene.utils import with_context

from core.models import Location


class LocationNode(DjangoNode):
    class Meta:
        model = Location
        # filter_fields = {
        #     'reservation': ['exact']
        # }


class Query(ObjectType):
    all_locations = DjangoFilterConnectionField(LocationNode)

    class Meta:
        abstract = True
