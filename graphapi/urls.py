from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from jwt_auth.mixins import JSONWebTokenAuthMixin

from graphene.contrib.django.views import GraphQLView

from graphapi.schema import schema


class AuthGraphQLView(JSONWebTokenAuthMixin, GraphQLView):
    pass

urlpatterns = [
    url(r'^graphql', csrf_exempt(AuthGraphQLView.as_view(schema=schema))),
    url(r'^graphiql', include('django_graphiql.urls')),
]
