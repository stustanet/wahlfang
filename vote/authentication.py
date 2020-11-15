from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.decorators import user_passes_test

from vote.models import Voter


def voter_login_required(function=None, redirect_field_name=None):
    """
    Decorator for views that checks that the voter is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and isinstance(u, Voter),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class AccessCodeBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        access_code = kwargs.pop('access_code', None)
        if access_code is None:
            return None

        voter_id, password = Voter.split_access_code(access_code)
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
                if not voter.logged_in:
                    voter.logged_in = True
                    voter.save()
                voter.backend = 'vote.authentication.AccessCodeBackend'
                return voter

        return None

    def get_user(self, user_id):
        return Voter.objects.filter(pk=user_id).first()
