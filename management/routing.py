from channels.routing import URLRouter
from django.urls import re_path
from . import consumers

websocket_urlpatterns = URLRouter([
    re_path(r'election/(?P<pk>\d+)$', consumers.ElectionConsumer.as_asgi()),
    re_path(r'meeting/(?P<pk>\d+)$', consumers.SessionConsumer.as_asgi()),
])
