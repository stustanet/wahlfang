from django.core.management.base import BaseCommand, CommandError

from vote.models import Voter


class Command(BaseCommand):
    help = 'Revoke the given access code'

    def add_arguments(self, parser):
        parser.add_argument('--access_code', type=str, required=True)

    def handle(self, *args, **options):
        access_code = options['access_code']
        voter_id, password = Voter.split_access_code(access_code)
        if not voter_id:
            raise CommandError("voter not found")

        voter = Voter.objects.get(pk=voter_id)

        if not voter.check_password(password):
            raise CommandError("incorrect access_code")

        voter.set_unusable_password()
        voter.save()

        if voter.has_usable_password():
            raise CommandError("unsetting password failed")

        self.stdout.write(
            self.style.SUCCESS('Successfully revoked access for "%s"\nAccess Code: %s' % (voter, access_code)))
