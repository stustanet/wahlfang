import os
from django.urls import reverse_lazy

# BASE_DIR = Path('/opt/wahlfang')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADMINS = (
    ('Wahlfang Admins', 'root@localhost')
)

DEBUG = False

# export application statistics such as http request duration / latency
# will also export # of manager accounts, # of sessions, # of elections
EXPORT_PROMETHEUS_METRICS = True


ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'vote',
    'management',
    'channels',
]

if EXPORT_PROMETHEUS_METRICS:
    INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

if EXPORT_PROMETHEUS_METRICS:
    MIDDLEWARE = ['django_prometheus.middleware.PrometheusBeforeMiddleware'] + \
                 MIDDLEWARE + \
                 ['django_prometheus.middleware.PrometheusAfterMiddleware']


ROOT_URLCONF = 'wahlfang.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = {
    'vote.authentication.AccessCodeBackend',
    'management.authentication.ManagementBackend',
    'management.authentication.ManagementBackendLDAP',
    'django.contrib.auth.backends.ModelBackend'
}

ASGI_APPLICATION = 'wahlfang.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

LOGIN_URL = reverse_lazy('vote:code_login')
LOGIN_REDIRECT_URL = reverse_lazy('vote:index')

RATELIMIT_KEY = 'ip'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/wahlfang/static'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Content Security Policy
# https://django-csp.readthedocs.io/en/latest/configuration.html#policy-settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:",)

# Mail
EMAIL_HOST = 'mail.stusta.de'
EMAIL_SENDER = 'no-reply@stusta.de'
EMAIL_PORT = 25

# File upload, etc...
MEDIA_ROOT = '/var/www/wahlfang/media'
MEDIA_URL = '/media/'

# LDAP
AUTH_LDAP_SERVER_URI = "ldap://ldap.stusta.de"
AUTH_LDAP_USER_DN_TEMPLATE = "cn=%(user)s,ou=account,ou=pnyx,dc=stusta,dc=mhn,dc=de"
AUTH_LDAP_START_TLS = True
AUTH_LDAP_USER_ATTR_MAP = {'email': 'mail'}
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
