import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from vote.models import Election, Session


class Command(BaseCommand):
    help = 'Creates a new election'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--title', type=str, required=True)
        parser.add_argument('-m', '--max-votes-yes', type=int, required=True)
        parser.add_argument('-i', '--session-id', type=int, required=True)

        # Make things a little bit easier for dev and debugging convenience
        if settings.DEBUG:
            parser.add_argument('-s', '--start-date', type=str, default=timezone.now())
            parser.add_argument('-a', '--application-due-date', type=str,
                                default=timezone.now() + datetime.timedelta(days=1))
            parser.add_argument('-e', '--end-date', type=str, default=timezone.now() + datetime.timedelta(days=2))
            parser.add_argument('-l', '--meeting-link', type=str, default="http://meeting.link")
            parser.add_argument('-d', '--meeting-time', type=str, default=timezone.now() + datetime.timedelta(days=3))
        else:
            parser.add_argument('-s', '--start-date', type=str, required=True)
            parser.add_argument('-a', '--application-due-date', type=str, required=True)
            parser.add_argument('-e', '--end-date', type=str, required=True)
            parser.add_argument('-l', '--meeting-link', type=str, required=True)
            parser.add_argument('-d', '--meeting-time', type=str, required=True)

    def handle(self, *args, **options):
        session = Session.objects.get(id=options['session_id'])
        election = Election.objects.create(
            title=options['title'],
            start_date=options['start_date'],
            end_date=options['end_date'],
            max_votes_yes=options['max_votes_yes'],
            session=session,
        )
        self.stdout.write(self.style.SUCCESS('Successfully created election "%s" with ID %i' % (election, election.id)))
