from django.test import TestCase

from vote.models import Enc32, Voter, Session


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
    session = Session.objects.create(
        title='Test session'
    )
    voter, access_code = Voter.from_data(
        email='spam@spam.spam',
        session=session
    )
    return voter, access_code
