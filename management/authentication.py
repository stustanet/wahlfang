from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.decorators import user_passes_test
from django_auth_ldap.backend import LDAPBackend

from management.models import ElectionManager


def management_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='management:login'):
    """
    Decorator for views that checks that the voter is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and isinstance(u, ElectionManager),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class ManagementBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        username = kwargs.pop('username', None)
        password = kwargs.pop('password', None)

        if username is None or password is None:
            return None

        try:
            user = ElectionManager.objects.get(username=username)
        except ElectionManager.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            ElectionManager().set_password(password)
        else:
            if user.check_password(password):
                user.backend = 'management.authentication.ManagementBackend'
                return user

        return None

    def get_user(self, user_id):
        return ElectionManager.objects.filter(pk=user_id).first()


class ManagementBackendLDAP(LDAPBackend):
    def get_user_model(self):
        return ElectionManager
