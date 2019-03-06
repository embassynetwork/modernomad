from .common import *  # noqa
from .common import INSTALLED_APPS

DEBUG = True
INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar'
]
SECRET_KEY = 'local_development'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True if DEBUG else False,
    'RESULTS_CACHE_SIZE': 100,
}
