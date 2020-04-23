import datetime

from django.test import TestCase
from django.utils import timezone

from vote.models import User, Election


def gen_token():
    election = Election.objects.create(
        title='Test election 2020',
        start_date=timezone.now(),
        end_date=timezone.now() + datetime.timedelta(days=10)
    )
    token = User.objects.create(
        first_name='Test',
        last_name='Test',
        email='spam@spam.spam',
        election=election
    )
    return token
