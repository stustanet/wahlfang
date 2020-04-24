from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User as DjangoUser

from vote.models import User


def token_login(function=None):
    """
    Decorator for views that checks that the user is with a token,
    redirecting to the login page if needed.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and User.user_exists(u.username),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class TokenBackend(BaseBackend):
    def authenticate(self, request, token=None):
        valid = User.user_exists(token)

        if not valid:
            return None

        user = DjangoUser.objects.get_or_create(username=token)[0]
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
