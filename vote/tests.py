from datetime import timedelta, datetime

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from vote.models import Election, Enc32, Voter, Session
from vote.selectors import closed_elections, open_elections, published_elections, upcoming_elections


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


class ElectionSelectorsTest(TestCase):
    def test_election_selectors(self) -> None:
        now = datetime(year=2021, month=4, day=1, tzinfo=timezone.get_fixed_timezone(5))
        before = now - timedelta(seconds=5)
        bbefore = now - timedelta(seconds=10)
        after = now + timedelta(seconds=5)
        freeze_time(now).start()

        session = Session.objects.create(title="TEST")
        # upcoming elections
        all_upcoming = set()
        all_upcoming.add(Election.objects.create(session=session))
        all_upcoming.add(Election.objects.create(session=session, start_date=after))
        # open elections
        all_opened = set()
        all_opened.add(Election.objects.create(session=session, start_date=now))
        all_opened.add(Election.objects.create(session=session, start_date=before, end_date=after))
        # published elections
        all_published = set()
        all_published.add(Election.objects.create(session=session, start_date=bbefore, end_date=before,
                                                  result_published=True))
        all_published.add(Election.objects.create(session=session, start_date=before, end_date=now,
                                                  result_published=True))
        # closed (not published) elections
        all_closed = set()
        all_closed.add(Election.objects.create(session=session, start_date=bbefore, end_date=before))
        all_closed.add(Election.objects.create(session=session, start_date=before, end_date=now))

        # test upcoming
        upcoming = upcoming_elections(session)
        self.assertEqual(all_upcoming, set(upcoming))
        for e in upcoming:
            self.assertTrue(not e.started and not e.closed and not e.is_open)

        # test open
        opened = open_elections(session)
        self.assertEqual(all_opened, set(opened))
        for e in opened:
            self.assertTrue(e.started and not e.closed and e.is_open)

        # test published
        published = published_elections(session)
        self.assertEqual(all_published, set(published))
        for e in published:
            self.assertTrue(e.started and e.closed and not e.is_open and e.result_published)

        # test closed
        closed = closed_elections(session)
        self.assertEqual(all_closed, set(closed))
        for e in closed:
            self.assertTrue(e.started and e.closed and not e.is_open and not e.result_published)


def gen_data():
    session = Session.objects.create(
        title='Test session'
    )
    voter, access_code = Voter.from_data(
        email='spam@spam.spam',
        session=session
    )
    return voter, access_code
