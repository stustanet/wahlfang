import os
import logging

from wahlfang.settings.base import *
from wahlfang.settings.wahlfang import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$rl7hy0b_$*7py@t0-!^%gdlqdv0f%1+h2s%rza@=2h#1$y1vw'

DEBUG = True
# will output to your console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Mail
EMAIL_HOST = 'mail.stusta.de'
EMAIL_SENDER = 'no-reply@stusta.de'
EMAIL_PORT = 25

# LDAP
AUTH_LDAP_SERVER_URI = "ldap://ldap.stusta.de"
AUTH_LDAP_USER_DN_TEMPLATE = "cn=%(user)s,ou=account,ou=pnyx,dc=stusta,dc=mhn,dc=de"
AUTH_LDAP_START_TLS = True
AUTH_LDAP_USER_ATTR_MAP = {'email': 'mail'}
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
