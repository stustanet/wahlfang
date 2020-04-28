import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from vote.models import Election


class Command(BaseCommand):
    help = 'Creates a new election'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, required=True)

    def handle(self, *args, **options):
        election = Election.objects.create(
            title=options['title'],
            start_date=timezone.now(),
            application_due_date=timezone.now() + datetime.timedelta(days=7),
            end_date=timezone.now() + datetime.timedelta(days=10),
            max_votes_yes=2,
        )
        self.stdout.write(self.style.SUCCESS('Successfully created election "%s" with ID %i' % (election, election.id)))
