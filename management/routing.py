from channels.routing import URLRouter
from django.urls import re_path
from . import consumers

websocket_urlpatterns = URLRouter([
    re_path(r'election/(?P<pk>\d+)$', consumers.CastVotesConsumer.as_asgi()),
    # TODO update voters logged in
])
