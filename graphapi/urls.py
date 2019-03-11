from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphapi.schema import schema


class AuthGraphQLView(GraphQLView):
    pass


urlpatterns = [
    url(r'^graphql', csrf_exempt(AuthGraphQLView.as_view(schema=schema)))
]
