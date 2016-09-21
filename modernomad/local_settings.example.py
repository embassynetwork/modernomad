# copy this file to local_settings.py. it should be exluded from the repo
# (ensure local_settings.py is in .gitignore)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'secret'

ADMINS = (
          ('Your Name', 'your@email.com'),
          )

ALLOWED_HOSTS = ['domain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'NAME': 'modernomadb',
        'PASSWORD': 'somepassword',
    }
}

MEDIA_ROOT = "../media"
BACKUP_ROOT = "../backups/"
BACKUP_COUNT = 30

# use XS_SHARING_ALLOWED_ORIGINS = '*' for all domains
XS_SHARING_ALLOWED_ORIGINS = "http://localhost:8989/"
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'PUT', 'OPTIONS', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"]

# what mode are we running in? use this to trigger different settings.
DEVELOPMENT = 0
PRODUCTION = 1

# default mode is dev. change to production as appropriate.
MODE = DEVELOPMENT

# how many days should people be allowed to make a booking request for?
MAX_BOOKING_DAYS = 14

# how many days ahead to send the welcome email to guests with relevan house
# info.
WELCOME_EMAIL_DAYS_AHEAD = 2

# this should be a TEST or PRODUCTION key depending on whether this is a local
# test/dev site or production!
STRIPE_SECRET_KEY = "sk_XXXXX"
STRIPE_PUBLISHABLE_KEY = "pk_XXXXX"

# Discourse discussion group
DISCOURSE_BASE_URL = 'http://your-discourse-site.com'
DISCOURSE_SSO_SECRET = 'paste_your_secret_here'

MAILGUN_API_KEY = "key-XXXX"

LIST_DOMAIN = "somedomain.com"

if MODE == DEVELOPMENT:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEBUG = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'somehost'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'some@email.com'
    EMAIL_HOST_PASSWORD = 'password'
    DEBUG = False

TEMPLATE_DEBUG = DEBUG

# fill in any local template directories. any templates with the same name WILL
# OVERRIDE included templates. don't forget the trailing slash in the path, and
# a comma at the end of the tuple item if there is only one path.
LOCAL_TEMPLATE_DIRS = (
                       # eg, "../local_templates/",
                       )

# celery configuration options
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/Users/jessykate/code/embassynetwork/logs/django.log',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'modernomad': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'gather': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
