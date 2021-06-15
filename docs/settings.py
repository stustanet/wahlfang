# Wahlfang configuration file.
# /etc/wahlfang/settings.py

from wahlfang.settings.base import *
from wahlfang.settings.wahlfang import *


#: Default list of admins who receive the emails from error logging.
ADMINS = (
    ('Mailman Suite Admin', 'root@localhost'),
)

# Postgresql datbase setup.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<db_name>',
        'USER': '<db_username>',
        'PASSWORD': '<password>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 'collectstatic' command will copy all the static files here.
# Alias this location from your webserver to `/static`
STATIC_ROOT = '/var/www/wahlfang/static'
# Alias this location from your webserver to `/media`
MEDIA_ROOT = '/var/www/wahlfang/media'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Make sure that this directory is created or Django will fail on start.
LOGGING['handlers']['file']['filename'] = '/var/log/wahlfang/wahlfang.log'

#: See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost",  # Good for debugging, keep it.
    # "lists.your-domain.org",
    # Add here all production domains you have.
]

SECRET_KEY = 'MyVerrySecretKey'  # FIXME: PLEASE CHANGE ME BEFORE DEPLOYING TO PRODUCTION

# Mail, see https://docs.djangoproject.com/en/3.2/topics/email/#email-backends for more options
EMAIL_HOST = '<your mail server>'
EMAIL_SENDER = '<your mail sender>'
EMAIL_PORT = 25

# LDAP, leave commented out to not use ldap authentication
# for more details see https://django-auth-ldap.readthedocs.io/en/latest/example.html

# AUTHENTICATION_BACKENDS = {
#     'vote.authentication.AccessCodeBackend',
#     'management.authentication.ManagementBackend',
#     'management.authentication.ManagementBackendLDAP',  # this authentication backend must be enabled for ldap auth
#     'django.contrib.auth.backends.ModelBackend'
# }
# AUTH_LDAP_SERVER_URI = "ldap://ldap.stusta.de"
# AUTH_LDAP_USER_DN_TEMPLATE = "cn=%(user)s,ou=account,ou=pnyx,dc=stusta,dc=mhn,dc=de"
# AUTH_LDAP_START_TLS = True
# AUTH_LDAP_USER_ATTR_MAP = {'email': 'mail'}
# AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True


# Wahlfang specific settings

# Whether to send election invitations / reminders from the Election Managers E-Mail or from `EMAIL_SENDER`
SEND_FROM_MANAGER_EMAIL = True
# List of valid domain names for your election managers emails in case `SEND_FROM_MANAGER_EMAIL` is True
# This has to be configured such that the mail server can actually send mails from the valid manager emails.
VALID_MANAGER_EMAIL_DOMAINS = []
URL = '<domain of your web server, e.g. "vote.stustanet.de">'
