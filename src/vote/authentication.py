from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User as DjangoUser

from vote.models import User


class TokenBackend(BaseBackend):
    def authenticate(self, request, token=None):
        voter = User.objects.filter(token=token).first()

        if not token:
            return None

        user = DjangoUser.objects.get_or_create(username=voter.token)[0]
        user.set_unusable_password()
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True

        # user.first_name = token.first_name
        # user.last_name = token.last_name
        user.save()

        return user

    def get_user(self, user_id):
        return DjangoUser.objects.filter(pk=user_id).first()
