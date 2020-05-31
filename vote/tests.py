import datetime

from django.test import TestCase
from django.utils import timezone

from vote.models import Enc32, Voter, Election


class Enc32TestCase(TestCase):
    def test_encoding(self):
        for voter_id in (0, 12345, 999999):
            e = Enc32.encode(voter_id)
            d = Enc32.decode(e)
            self.assertEqual(voter_id, d)

class VoterTestCase(TestCase):
    def test_access_code(self):
        for voter_id in (0, 12345, 999999):
            raw_password = Enc32.alphabet
            code = Voter.get_access_code(voter_id, raw_password)
            ret_voter_id, ret_password = Voter.split_access_code(code)
            self.assertEqual(voter_id, ret_voter_id)
            self.assertEqual(raw_password, ret_password)

def gen_data():
    election = Election.objects.create(
        title='Test election 2020',
        start_date=timezone.now(),
        application_due_date=timezone.now() + datetime.timedelta(days=7),
        end_date=timezone.now() + datetime.timedelta(days=10),
        max_votes_yes=2,
    )
    voter, access_code = Voter.from_data(
        voter_id='012345',
        room='123',
        email='spam@spam.spam',
        election=election
    )
    return voter, access_code
