import re

from django.utils.text import compress_string
from django.utils.cache import patch_vary_headers

from django import http

''' 
EXAMPLE USAGE:
    Put this file in a directory called, eg, 'middleware,' inside your django
    project. Make sure to create an __init__.py file in the directory so it can
    be included as a module. 
    Set the values for 
        settings.XS_SHARING_ALLOWED_ORIGINS
        settings.XS_SHARING_ALLOWED_METHODS 
        settings.XS_SHARING_ALLOWED_HEADERS
    in settings.py. Then include 
        'modernomad.middleware.crossdomainxhr.CORSMiddleware' 
    in MIDDLEWARE_CLASSES in settings.py.
'''

try:
    from django.conf import settings 
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
    XS_SHARING_ALLOWED_HEADERS = settings.XS_SHARING_ALLOWED_HEADERS
except:
    XS_SHARING_ALLOWED_ORIGINS = ''
    XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
    XS_SHARING_ALLOWED_HEADERS = []


class CORSMiddleware(object):
    """
        This middleware allows cross-domain XHR using the html5 postMessage API.

        eg:
        Access-Control-Allow-Origin: http://foo.example
        Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
        Access-Control-Allow-Methods: ["Content-Type"]

    """
    def process_request(self, request):

        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS ) 
            response['Access-Control-Allow-Headers']  = ",".join( XS_SHARING_ALLOWED_HEADERS )
            return response

        return None

    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
        response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )

        return response
