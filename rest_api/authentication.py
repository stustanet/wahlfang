from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from management.models import ElectionManager
from vote.models import Voter


class GenericUserModelJWTAuthentication(JWTAuthentication):

    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if token.payload[settings.JWT_CLAIM_USER_TYPE] != self.user_model.__name__:
            raise AuthenticationFailed(_('wrong token type'), code='token_type_mismatch')

        return token


class VoterJWTAuthentication(GenericUserModelJWTAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = Voter


class ElectionManagerJWTAuthentication(GenericUserModelJWTAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = ElectionManager


class IsVoter(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(isinstance(request.user, Voter) and request.user.is_authenticated)


class IsElectionManager(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(isinstance(request.user, ElectionManager) and request.user.is_authenticated)
