from .common import *　# noqa
from .common import env
from .common import BASE_DIR

SECRET_KEY = env('SECRET_KEY')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
        },
    },
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',
        'CACHE': True,
        'STATS_FILE': BASE_DIR / 'client/webpack-stats-prod.json',
    }
}
