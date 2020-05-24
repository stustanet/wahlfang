from django.core.management.base import BaseCommand

from management.models import ElectionManager


class Command(BaseCommand):
    help = 'Create a new management login'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--email', type=str, required=True)
        parser.add_argument('-p', '--password', type=str, required=True)

    def handle(self, *args, **options):
        manager = ElectionManager(
            email=options['email']
        )
        manager.set_password(options['password'])
        manager.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully created management login with email {options["email"]}'))
