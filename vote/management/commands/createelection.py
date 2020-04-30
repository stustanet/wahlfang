from django.core.management.base import BaseCommand

from vote.models import Election


class Command(BaseCommand):
    help = 'Creates a new election'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--title', type=str, required=True)
        parser.add_argument('-s', '--start-date', type=str, required=True)
        parser.add_argument('-a', '--application-due-date', type=str, required=True)
        parser.add_argument('-e', '--end-date', type=str, required=True)
        parser.add_argument('-m', '--max-votes-yes', type=int, required=True)
        parser.add_argument('-d', '--description', type=str, required=True)

    def handle(self, *args, **options):
        election = Election.objects.create(
            title=options['title'],
            start_date=options['start_date'],
            application_due_date=options['application_due_date'],
            end_date=options['end_date'],
            max_votes_yes=options['max_votes_yes'],
            description=options['description']
        )
        self.stdout.write(self.style.SUCCESS('Successfully created election "%s" with ID %i' % (election, election.id)))
