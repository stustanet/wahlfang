from django.conf import settings
from django.core.management.base import BaseCommand

from vote.models import Session, Voter


class Command(BaseCommand):
    help = 'Creates a new Voter'

    def add_arguments(self, parser):
        parser.add_argument('--session-id', type=int, required=True)
        parser.add_argument('--no-invitation', default=False, action='store_true')

        # Make things a little bit easier for dev and debugging convenience
        if settings.DEBUG:
            parser.add_argument('--email', type=str, default="spam@spam.spam")
        else:
            parser.add_argument('--email', type=str, required=True)

    def handle(self, *args, **options):
        session = Session.objects.get(pk=options['session_id'])

        voter, access_code = Voter.from_data(
            email=options['email'],
            session=session,
        )
        if not options['no_invitation']:
            voter.send_invitation(access_code, session.managers.all().first().sender_email)
        self.stdout.write(self.style.SUCCESS('Successfully created voter "%s"\nAccess Code: %s' % (voter, access_code)))
