from urllib.parse import parse_qs

from django.conf import settings
from channels.db import database_sync_to_async
from django.db import close_old_connections
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from management.models import ElectionManager
from vote.models import Voter


class WebsocketJWTAuthMiddleware:
    """
    Custom token auth middleware
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):

        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        # Get the token
        qs = parse_qs(scope["query_string"].decode("utf8"))
        if "token" not in qs:
            return None
        token = qs["token"][0]

        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Will return a dictionary like -
            # {
            #     "token_type": "access",
            #     "exp": 1568770772,
            #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
            #     "user_id": 6
            # }

            # Get the user using ID
            if decoded_data['user_type'] == Voter.__name__:
                scope['user'] = await database_sync_to_async(Voter.objects.get)(voter_id=decoded_data["user_id"])
            elif decoded_data['user_type'] == ElectionManager.__name__:
                scope['user'] = await database_sync_to_async(ElectionManager.objects.get)(id=decoded_data["user_id"])
            else:
                return None

        # Return the inner application directly and let it run everything else
        return await self.app(scope, receive, send)
