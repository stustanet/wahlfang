"""
WSGI config for wahlfang project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from wahlfang.manage import setup

setup()
application = get_wsgi_application()
