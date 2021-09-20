from channels.routing import URLRouter
from django.urls import path

from . import consumers

websocket_urlpatterns = URLRouter([
    path('vote/', consumers.VoteAPIConsumer.as_asgi()),
    path('management/', consumers.ManagementAPIConsumer.as_asgi())
])
