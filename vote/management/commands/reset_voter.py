from django.core.management.base import BaseCommand

from vote.models import Voter


class Command(BaseCommand):
    help = 'Reset Voter and resend invitation'

    def add_arguments(self, parser):
        parser.add_argument('--voter_id', type=int, required=True)
        parser.add_argument('--email', type=str)
        parser.add_argument('--send-invitation', type=bool, default=True)

    def handle(self, *args, **options):
        voter_id = options['voter_id']
        voter = Voter.objects.get(pk=voter_id)
        password = voter.set_password()

        email = options['email']
        if email:
            voter.email = email
            self.stdout.write(self.style.SUCCESS('New email: "%s"' % email))

        voter.save()

        access_code = Voter.get_access_code(voter_id, password)
        if options['send_invitation']:
            voter.send_invitation(access_code, voter.session.managers.all().first().sender_email)
        self.stdout.write(self.style.SUCCESS('Successfully reset voter "%s"\nAccess Code: %s' % (voter, access_code)))
