from channels.routing import URLRouter
from django.urls import re_path
from . import consumers
# TODO

websocket_urlpatterns = URLRouter([
    # re_path(r'', consumers),
])
