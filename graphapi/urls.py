from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from graphene.contrib.django.views import GraphQLView

from graphapi.schema import schema

urlpatterns = [
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(schema=schema))),
    url(r'^graphiql', include('django_graphiql.urls')),
]
