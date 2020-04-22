import datetime

from django.test import TestCase
from django.utils import timezone

from vote.models import Token, Election


def gen_token():
    election = Election.objects.create(
        title='Test election 2020',
        start_date=timezone.now(),
        end_date=timezone.now() + datetime.timedelta(days=10)
    )
    token = Token.objects.create(
        email='spam@spam.spam',
        election=election
    )
    return token
