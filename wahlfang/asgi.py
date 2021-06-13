"""
ASGI config for wahlfang project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

from wahlfang.manage import setup

setup()
django_asgi_application = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
import wahlfang.routing

application = ProtocolTypeRouter({
    "https": django_asgi_application,
    "websocket": AuthMiddlewareStack(wahlfang.routing.websocket_urlpatterns),
})
