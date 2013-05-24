# copy this file to local_settings.py. it should be exluded from the repo
# (ie, ensure local_settings.py is in .gitignore)

ADMINS += (
	('Jessy Kate Schingler', 'jessy@jessykate.com'),
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd+xvh@)+d_iw%%w65+61&amp;2(w7upu*rt7l%n3d_li#1^pt@133^'

# use XS_SHARING_ALLOWED_ORIGINS = '*' for all domains
XS_SHARING_ALLOWED_ORIGINS = "http://localhost:8989/"
XS_SHARING_ALLOWED_METHODS = ['POST','GET', 'PUT', 'OPTIONS', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"]

# what mode are we running in? use this to trigger different settings. 
DEVELOPMENT = 0
PRODUCTION = 1

# default mode is dev. change to production as appropriate. 
MODE = DEVELOPMENT

# how many days should people be allowed to make a reservation request for?
MAX_RESERVATION_DAYS = 14

# if using stripe, enter your stripe *secret* key here
STRIPE_SECRET_KEY = "insert your key here"
STRIPE_PUBLISHABLE_KEY = "insert your key here"

if MODE == DEVELOPMENT:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEBUG=True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'   
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'user@domain.com'
    EMAIL_HOST_PASSWORD = 'password'
    DEBUG=False

TEMPLATE_DEBUG = DEBUG

# this will be used as the subject line prefix for all emails sent from this app. 
EMAIL_SUBJECT_PREFIX = "[Your House Name Here]"
DEFAULT_FROM_EMAIL = 'stay@embassynetwork.com'

# social media
TWITTER = "your twitter handle"
FACEBOOK_GROUP = "your facebook group"
EVENTS_LINK = "main events link"

# celery configuration options
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
