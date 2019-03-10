import re
from django.conf import settings
from basicauth.middleware import BasicAuthMiddleware as BaseBasicAuthMiddleware


# https://github.com/hirokiky/django-basicauth/issues/10
class BasicAuthMiddleware(BaseBasicAuthMiddleware):
    def process_request(self, request):
        always_allow_urls = map(
            re.compile, getattr(settings, "BASICAUTH_ALWAYS_ALLOW_URLS", [])
        )
        for allowed_url in always_allow_urls:
            if allowed_url.search(request.path):
                return None

        return super().process_request(request)
