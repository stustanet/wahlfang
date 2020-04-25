import string

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.decorators import user_passes_test

from vote.models import Voter


def voter_login_required(function=None):
    """
    Decorator for views that checks that the voter is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and isinstance(u, Voter)
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class AccessCodeBackend(BaseBackend):
    def authenticate(self, request, access_code=None):
        if access_code is None:
            return None

        voter_id, password = self.split_access_code(access_code)
        if not voter_id:
            return None

        try:
            voter = Voter.objects.get(voter_id=voter_id)
        except Voter.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            Voter().set_password(password)
        else:
            if voter.check_password(password):
                return voter

    @classmethod
    def split_access_code(cls, access_code=None):
        if not access_code:
            return (None, None)

        access_code = access_code.replace('-', '')
        if len(access_code) < 6 or not all(c in string.hexdigits for c in access_code):
            return (None, None)

        voter_id = int(access_code[:5], 16)
        password = access_code[5:].lower()
        return (voter_id, password)

    def get_user(self, user_id):
        return Voter.objects.filter(pk=user_id).first()
