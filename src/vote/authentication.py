from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from vote.models import Token


class TokenBackend(BaseBackend):
    def authenticate(self, request, token=None):
        token = Token.objects.filter(uuid=token).first()

        if not token:
            return None

        user = User.objects.get_or_create(username=token.uuid)[0]
        user.set_unusable_password()
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True

        # user.first_name = token.first_name
        # user.last_name = token.last_name
        user.save()

        return user

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id).first()
