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

from channels.auth import AuthMiddlewareStack  # pylint: disable=wrong-import-order
from channels.routing import ProtocolTypeRouter  # pylint: disable=wrong-import-order
import wahlfang.routing  # pylint: disable=wrong-import-order

application = ProtocolTypeRouter({
    "https": django_asgi_application,
    "websocket": AuthMiddlewareStack(wahlfang.routing.websocket_urlpatterns),
})
