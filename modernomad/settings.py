# Django settings for modernomad project.
import os

# Make filepaths relative to settings.
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

BACKUP_ROOT = ROOT + '/backups/'

ADMINS = (
    ('Jessy Kate Schingler', 'jessy@embassynetwork.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'modernomad.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
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
MEDIA_ROOT = path("../media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path("../../static/")
STATICFILES_DIRS = ('static', )
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

AUTHENTICATION_BACKENDS = (
	'modernomad.backends.EmailOrUsernameModelBackend',
	'django.contrib.auth.backends.ModelBackend'
)

EMAIL_BACKEND = 'modernomad.backends.MailgunBackend'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'modernomad.middleware.crossdomainxhr.CORSMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

#default template context processors
TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages",
	"core.context_processors.location.network_locations",
	"core.context_processors.analytics.google_analytics",
)

ROOT_URLCONF = 'modernomad.urls.main'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'modernomad.wsgi.application'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	path("../templates/"),
	path("core/templates/"),
)

INSTALLED_APPS = (
	'registration',
	'south',
	'core',
	'djcelery',
	'gather',
	'modernomad',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
)

AUTH_PROFILE_MODULE = 'core.UserProfile'
ACCOUNT_ACTIVATION_DAYS = 7  # One week account activation window.

# If we add a page for the currently-logged-in user to view and edit
# their profile, we might want to use that here instead.
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/people/login/'
LOGOUT_URL = '/people/logout/'

# Celery configuration options
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_ACCEPT_CONTENT = ['json', 'yaml']

# import any local settings
try:
	from local_settings import *
	TMP_TEMPLATE_DIRS = ()
	for local_tmpl_dir in LOCAL_TEMPLATE_DIRS:
		TMP_TEMPLATE_DIRS += (path(local_tmpl_dir),)
	# make sure any local overrides are found first before the default
	# templates
	TEMPLATE_DIRS = TMP_TEMPLATE_DIRS + TEMPLATE_DIRS
except ImportError:
	pass

