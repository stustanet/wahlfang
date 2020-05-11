from django.conf import settings
from django.core.management.base import BaseCommand

from vote.models import Election, Voter


class Command(BaseCommand):
    help = 'Creates a new Voter'

    def add_arguments(self, parser):
        parser.add_argument('--election_id', type=int, required=True)
        parser.add_argument('--voter_id', type=int, required=True)
        parser.add_argument('--no_vote', default=False, action='store_true')
        parser.add_argument('--no_invitation', default=False, action='store_true')

        # Make things a little bit easier for dev and debugging convenience
        if settings.DEBUG:
            parser.add_argument('--first_name', type=str, default="First")
            parser.add_argument('--last_name', type=str, default="Last")
            parser.add_argument('--room', type=str, default="123")
            parser.add_argument('--email', type=str, default="spam@spam.spam")
        else:
            parser.add_argument('--first_name', type=str, required=True)
            parser.add_argument('--last_name', type=str, required=True)
            parser.add_argument('--room', type=str, required=True)
            parser.add_argument('--email', type=str, required=True)

    def handle(self, *args, **options):
        election = Election.objects.get(pk=options['election_id'])

        voter, access_code = Voter.from_data(
            voter_id=options['voter_id'],
            first_name=options['first_name'],
            last_name=options['last_name'],
            room=options['room'],
            email=options['email'],
            election=election,
            voted=options['no_vote'],
        )
        if not options['no_invitation']:
            voter.send_invitation(access_code)
        self.stdout.write(self.style.SUCCESS('Successfully created voter "%s"\nAccess Code: %s' % (voter, access_code)))
