from channels.routing import URLRouter
from django.urls import path

import management.routing
import wahlfang_api.routing
import vote.routing

websocket_urlpatterns = URLRouter([
    path('', vote.routing.websocket_urlpatterns),
    path('api/v1/', wahlfang_api.routing.websocket_urlpatterns),
    path('management/', management.routing.websocket_urlpatterns),
])
