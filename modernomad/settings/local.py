from .common import *  # noqa
from .common import INSTALLED_APPS

DEBUG = True
INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar'
]
SECRET_KEY = 'local_development'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'modernomad',
        'NAME': 'modernomad',
        'PASSWORD': '',
    }
}

