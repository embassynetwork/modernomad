# A sensible set of defaults for a production environment which can be
# overridden with environment variables

import environ
from django.core.exceptions import ImproperlyConfigured
import os
from .settings import *

env = environ.Env()

# what mode are we running in? use this to trigger different settings.
DEVELOPMENT = 0
PRODUCTION = 1

# default mode is production. change to dev as appropriate.
env_mode = env('MODE', default='PRODUCTION')
if env_mode == 'DEVELOPMENT':
    MODE = DEVELOPMENT
    DEBUG = True
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
elif env_mode == 'PRODUCTION':
    MODE = PRODUCTION
    DEBUG = False

    STATIC_ROOT = path("static_root/")

    # Collect static gathers client/dist/ into root of static/,
    # which is why bundle dir is blank
    WEBPACK_LOADER = {
        'DEFAULT': {
            'BUNDLE_DIR_NAME': '',
            'CACHE': True,
            'STATS_FILE': os.path.join(BASE_DIR, 'client/webpack-stats-prod.json'),
        }
    }
    COMPRESS_OFFLINE = True
else:
    raise ImproperlyConfigured('Unknown MODE setting')

TEMPLATE_DEBUG = DEBUG

SECRET_KEY = env('SECRET_KEY')
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://postgres@postgres/postgres'),
}

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

BROKER_URL = env('BROKER_URL', default=env('CLOUDAMQP_URL', default='amqp://guest:guest@rabbitmq//'))
CELERY_RESULT_BACKEND = BROKER_URL

# this should be a TEST or PRODUCTION key depending on whether this is a local
# test/dev site or production!
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')

# Discourse discussion group
DISCOURSE_BASE_URL = env('DISCOURSE_BASE_URL', default='')
DISCOURSE_SSO_SECRET = env('DISCOURSE_SSO_SECRET', default='')

ADMINS = ((
    env('ADMIN_NAME', default='Unnamed'),
    env('ADMIN_EMAIL', default='none@example.com')
),)

MAILGUN_API_KEY = env('MAILGUN_API_KEY', default='')
LIST_DOMAIN = env('LIST_DOMAIN', default='somedomain.com')
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='[Modernomad] ')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='stay@example.com')

GOOGLE_ANALYTICS_PROPERTY_ID = env('GOOGLE_ANALYTICS_PROPERTY_ID', default='')
GOOGLE_ANALYTICS_DOMAIN = env('GOOGLE_ANALYTICS_DOMAIN', default='example.com')

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

# Media storage
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_DEFAULT_ACL = 'public-read'
if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = env('MEDIA_URL', default='https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME)

