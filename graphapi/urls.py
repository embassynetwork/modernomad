from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from jwt_auth.mixins import JSONWebTokenAuthMixin
from graphene.contrib.django.views import GraphQLView
from graphapi.schema import schema
from jwt_auth.utils import get_authorization_header


class OptionalJWTMixin(JSONWebTokenAuthMixin):
    def dispatch(self, request, *args, **kwargs):
        auth = get_authorization_header(request)
        if auth:
            return super(OptionalJWTMixin, self).dispatch(request, *args, **kwargs)
        else:
            return super(JSONWebTokenAuthMixin, self).dispatch(request, *args, **kwargs)


class AuthGraphQLView(OptionalJWTMixin, GraphQLView):
    pass

urlpatterns = [
    url(r'^graphql', csrf_exempt(AuthGraphQLView.as_view(schema=schema))),
    url(r'^graphiql', include('django_graphiql.urls')),
]
