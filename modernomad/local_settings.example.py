# copy this file to local_settings.py. it should be exluded from the repo
# (ensure local_settings.py is in .gitignore)

# use XS_SHARING_ALLOWED_ORIGINS = '*' for all domains
XS_SHARING_ALLOWED_ORIGINS = "http://localhost:8989/"
XS_SHARING_ALLOWED_METHODS = ['POST','GET', 'PUT', 'OPTIONS', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["Content-Type"]
