import sys
from .common import *  # noqa
from .common import INSTALLED_APPS, MIDDLEWARE_CLASSES

DEBUG = True
RUNNING_TESTS = 'test' in sys.argv

if not RUNNING_TESTS:
    INSTALLED_APPS += [
        'debug_toolbar'
    ]
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware', )

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True if DEBUG else False,
        'RESULTS_CACHE_SIZE': 100,
    }

SECRET_KEY = 'local_development'

