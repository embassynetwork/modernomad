import sys
from .common import *  # noqa
from .common import INSTALLED_APPS, MIDDLEWARE_CLASSES

DEBUG = True
TESTING_MODE = 'test' in sys.argv
DEV_MODE = DEBUG and not TESTING_MODE

if DEV_MODE:
    INSTALLED_APPS += [
        'debug_toolbar'
    ]
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware', )

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True if DEBUG else False,
        'RESULTS_CACHE_SIZE': 100,
    }

SECRET_KEY = 'local_development'

