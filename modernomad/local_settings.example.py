# copy this file to local_settings.py. it should be exluded from the repo
# (ie, ensure local_settings.py is in .gitignore)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd+xvh@)+d_iw%%w65+61&amp;2(w7upu*rt7l%n3d_li#1^pt@133^'

# use XS_SHARING_ALLOWED_ORIGINS = '*' for all domains
XS_SHARING_ALLOWED_ORIGINS = "http://localhost:8989/"
XS_SHARING_ALLOWED_METHODS = ['POST','GET', 'PUT', 'OPTIONS', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"]

# email settings - example only! will send emails to console if left untouched. 
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_PORT = "1025"
EMAIL_HOST = "localhost"