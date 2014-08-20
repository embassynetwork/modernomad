# copy this file to local_settings.py. it should be exluded from the repo
# (ie, ensure local_settings.py is in .gitignore)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'yourownprivatekeythatnooneelseknowsbutyou'

# use XS_SHARING_ALLOWED_ORIGINS = '*' for all domains
XS_SHARING_ALLOWED_ORIGINS = "http://localhost:8989/"
XS_SHARING_ALLOWED_METHODS = ['POST','GET', 'PUT', 'OPTIONS', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"]

# required for django-gather app
#LOCATION_MODEL = 'gather.Location'
LOCATION_MODEL = 'core.Location'

# if using stripe, enter your stripe *secret* key here
STRIPE_SECRET_KEY = "insert your key here"
STRIPE_PUBLISHABLE_KEY = "insert your key here"

MAILGUN_API_KEY = "your private key from mailgun"
LIST_DOMAIN = "the mail domain used for sending and receiving via mailgun - eg. mail.housename.com"

ALLOWED_HOSTS=['localhost', '127.0.0.1', ]
TEMPLATE_DEBUG = True
DEBUG=True

# fill in any local template directories. any templates with the same name WILL
# OVERRIDE included templates. don't forget the trailing slash in the path, and
# a comma at the end of the tuple item if there is only one path. 
LOCAL_TEMPLATE_DIRS = (
	# eg, "../local_templates/",
)

# this will be used as the subject line prefix for all emails sent from this app. 
EMAIL_SUBJECT_PREFIX = "[Embassy Network] "
DEFAULT_FROM_EMAIL = 'stay@embassynetwork.com'

# Google analytics
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-14845987-3'
GOOGLE_ANALYTICS_DOMAIN = 'mydomain.com'

# celery configuration options
# note!! you must add the broker and broker user to rabbitmq that corresponds
# to these credentials. this is done by:
# sudo rabbitmqctl add_user myusername mypassword
# sudo rabbitmqctl add_vhost myvhost
# sudo rabbitmqctl set_permissions -p myvhost myusername ".*" ".*" ".*"
# and then you MUST restart rabbitmq:
# sudo rabbitmqctl reset
#BROKER_URL = 'amqp:myusername:mypassword@hostname/vhost'

