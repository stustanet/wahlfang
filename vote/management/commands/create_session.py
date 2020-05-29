from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from vote.models import Session


class Command(BaseCommand):
    help = 'Creates a new election'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--title', type=str, required=True)

        # Make things a little bit easier for dev and debugging convenience
        if settings.DEBUG:
            parser.add_argument('-s', '--start-date', type=str, default=timezone.now())
            parser.add_argument('-l', '--meeting-link', type=str, default="http://meeting.link")
            parser.add_argument('-id', type=int, default=0)
        else:
            parser.add_argument('-s', '--start-date', type=str, required=True)
            parser.add_argument('-l', '--meeting-link', type=str, required=True)

    def handle(self, *args, **options):
        session = Session.objects.create(
            id=options['id'],
            title=options['title'],
            start_date=options['start_date'],
            meeting_link=options['meeting_link'],
        )
        self.stdout.write(self.style.SUCCESS('Successfully created session "%s" with ID %i' % (session, session.id)))
