# Django settings for modernomad project.
import os
import datetime
import sys
from pathlib import Path
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()

BASE_DIR = Path.cwd()
BACKUP_ROOT = BASE_DIR / 'backups'

ADMINS = ((
    env('ADMIN_NAME', default='Unnamed'),
    env('ADMIN_EMAIL', default='none@example.com')
),)

MANAGERS = ADMINS
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

DEBUG = False

STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///modernomad.db'),
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = BASE_DIR / 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

AWS_STORAGE_BUCKET_NAME = env('BUCKETEER_BUCKET_NAME', default='')
AWS_ACCESS_KEY_ID = env('BUCKETEER_AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('BUCKETEER_AWS_SECRET_ACCESS_KEY', default='')
AWS_DEFAULT_ACL = 'public-read'
if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = env('MEDIA_URL', default='https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME)
    AWS_LOCATION = 'public/'

SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    print("Found Sentry DSN")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), sentry_logging]
    )


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = ('client/dist',)
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

AUTHENTICATION_BACKENDS = (
    'modernomad.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)

EMAIL_BACKEND = 'modernomad.backends.MailgunBackend'
MAILGUN_API_KEY = env('MAILGUN_API_KEY', default='')

# this will be used as the subject line prefix for all emails sent from this app.
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='[Modernomad] ')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='stay@example.com')
LIST_DOMAIN = env('LIST_DOMAIN', default='somedomain.com')

GOOGLE_ANALYTICS_PROPERTY_ID = env('GOOGLE_ANALYTICS_PROPERTY_ID', default='')
GOOGLE_ANALYTICS_DOMAIN = env('GOOGLE_ANALYTICS_DOMAIN', default='example.com')

TEMPLATES = [
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS' : [
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        BASE_DIR / 'templates',
        BASE_DIR / 'core' / 'templates'
    ],
    # default template context processors
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.debug",
            "django.template.context_processors.i18n",
            "django.template.context_processors.media",
            "django.template.context_processors.static",
            "django.template.context_processors.tz",
            "django.template.context_processors.request",
            "django.contrib.messages.context_processors.messages",
            "core.context_processors.location.location_variables",
            "core.context_processors.location.network_locations",
            "core.context_processors.analytics.google_analytics",
        ],
    },
},
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'modernomad.middleware.crossdomainxhr.CORSMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# other JWT options available at https://github.com/jpadilla/django-jwt-auth
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1000)

ROOT_URLCONF = 'modernomad.urls.main'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'modernomad.wsgi.application'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'client/build/',
        'STATS_FILE': BASE_DIR / 'client' / 'webpack-stats.json',
    }
}

INSTALLED_APPS = [
    # django stuff
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.admindocs',
    'django.contrib.humanize',

    # 3rd party
    'compressor',
    'django_behave',
    'django_extensions',
    'django_filters',
    'djcelery',
    'graphene_django',
    'rest_framework',
    'webpack_loader',

    # modernomad
    'core',
    'bank',
    'gather',
    'modernomad',
    'api',
    'bdd',
    'graphapi',
]

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

# FIXME: disabled. see https://github.com/embassynetwork/modernomad/issues/302
# TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

AUTH_PROFILE_MODULE = 'core.UserProfile'
ACCOUNT_ACTIVATION_DAYS = 7  # One week account activation window.

# If we add a page for the currently-logged-in user to view and edit
# their profile, we might want to use that here instead.
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/people/login/'
LOGOUT_URL = '/people/logout/'

# Celery configuration options
BROKER_URL = env(
    'BROKER_URL',
    default=env('CLOUDAMQP_URL', default='amqp://guest:guest@localhost:5672//')
)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_ACCEPT_CONTENT = ['json', 'yaml']

# Disabled when moving to Heroku for simplicity's sake, because no tasks 
# have results. If results are needed, a suitable one can be picked for
# Heroku + CloudAMPQ. (Probably the "rpc" one, perhaps Django ORM?)
CELERY_RESULT_BACKEND = None

# as per https://www.cloudamqp.com/docs/celery.html
BROKER_POOL_LIMIT = 1
BROKER_HEARTBEAT = None
BROKER_CONNECTION_TIMEOUT = 30
CELERY_EVENT_QUEUE_EXPIRES = 60
CELERYD_PREFETCH_MULTIPLIER = 1

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

NOSE_ARGS = [
    '--nocapture',
    '--nologcapture'
]

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
}


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


TESTS_IN_PROGRESS = False
if 'test' in sys.argv[1:]:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    TESTS_IN_PROGRESS = True
    MIGRATION_MODULES = DisableMigrations()

os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = "localhost:8000-8010,8080,9200-9300"

# Setting unique=True on a ForeignKey has the same effect as using a OneToOneField.
SILENCED_SYSTEM_CHECKS = ["fields.W342"]
