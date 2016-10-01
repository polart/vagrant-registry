from .base import *


DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY', '')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'vagrant_registry'),
        'USER': os.environ.get('DB_USER', 'vagrant_registry'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'vagrant_registry'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = 'DENY'

SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = PROTECTED_MEDIA_ROOT
SENDFILE_URL = PROTECTED_MEDIA_URL

if os.environ.get('BEHIND_HTTPS_PROXY', False) == 'true':
    # WARNING! This should be used only behind HTTPS proxy,
    # other than from the Docker image! Docker image Nginx server
    # handles only HTTP requests. In order to serve the site on HTTPS
    # another proxy server can be used to handle all the HTTPS stuff.
    # And this setting should be turned on to tell Django, that
    # traffic on HTTP is secure.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')
