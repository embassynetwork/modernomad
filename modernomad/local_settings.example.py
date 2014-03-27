# copy this file to local_settings.py. it should be exluded from the repo
# (ie, ensure local_settings.py is in .gitignore)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd+xvh@)+d_iw%%w65+61&amp;2(w7upu*rt7l%n3d_li#1^pt@133^'

# use XS_SHARING_ALLOWED_ORIGINS = '*' for all domains
XS_SHARING_ALLOWED_ORIGINS = "http://localhost:8989/"
XS_SHARING_ALLOWED_METHODS = ['POST','GET', 'PUT', 'OPTIONS', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"]

# what mode are we running in? use this to trigger different settings. 
DEVELOPMENT = 0
PRODUCTION = 1

# What is the name of this house, building, establishment, etc.?
LOCATION_NAME = "Embassy SF"
LOCATION_ADDRESS = "399 Webster Street, San Francisco, 94117"

# HOUSE INFO
SSID = "Your wireless network name"
SSID_PASSWORD = "your wireness network password"

# default mode is dev. change to production as appropriate. 
MODE = DEVELOPMENT

# how many days should people be allowed to make a reservation request for?
MAX_RESERVATION_DAYS = 14

# how many days ahead to send the welcome email to guests with relevan house
# info.
WELCOME_EMAIL_DAYS_AHEAD = 2

# if your house has a private access code, enter it here. 
HOUSE_ACCESS_CODE = "1234"

# if using stripe, enter your stripe *secret* key here
STRIPE_SECRET_KEY = "insert your key here"
STRIPE_PUBLISHABLE_KEY = "insert your key here"

MAILGUN_API_KEY = "your private key from mailgun"
LIST_DOMAIN = "the mail domain used for sending and receiving via mailgun - eg. mail.housename.com"

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

# fill in any local template directories. any templates with the same name WILL
# OVERRIDE included templates. don't forget the trailing slash in the path, and
# a comma at the end of the tuple item if there is only one path. 
LOCAL_TEMPLATE_DIRS = (
	# eg, "../local_templates/",
)

# this will be used as the subject line prefix for all emails sent from this app. 
EMAIL_SUBJECT_PREFIX = "[Your House Name Here]"
DEFAULT_FROM_EMAIL = 'stay@embassynetwork.com'

# social media
TWITTER = "your twitter handle"
FACEBOOK_GROUP = "your facebook group"
EVENTS_LINK = "main events link"

# eventbrite
EVENTBRITE_APP_KEY = "your app key here"
EVENTBRITE_USER_KEY = "your user key here"

# celery configuration options
# note!! you must add the broker and broker user to rabbitmq that corresponds
# to these credentials. this is done by:
# sudo rabbitmqctl add_user myusername mypassword
# sudo rabbitmqctl add_vhost myvhost
# sudo rabbitmqctl set_permissions -p myvhost myusername ".*" ".*" ".*"
# and then you MUST restart rabbitmq:
# sudo rabbitmqctl reset
BROKER_URL = 'amqp:myusername:mypassword@hostname/vhost'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
