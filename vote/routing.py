from channels.routing import URLRouter
from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = URLRouter([
    path('', consumers.VoteConsumer.as_asgi()),
    re_path(r'spectator/(?P<uuid>.+)$', consumers.VoteConsumer.as_asgi()),
])
