from tastypie.authorization import Authorization
from tastypie.resources import ModelResource


from core.models import House, Resource, UserProfile, Endorsement


class HouseResource(ModelResource):
    class Meta:
        queryset = House.objects.all()


class ResourceResource(ModelResource):
    class Meta:
        queryset = Resource.objects.all()


class UserResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()


class EndorsementResource(ModelResource):
    class Meta:
        queryset = Endorsement.objects.all()
