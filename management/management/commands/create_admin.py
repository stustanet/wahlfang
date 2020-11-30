from getpass import getpass
from secrets import token_hex

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from management.models import ElectionManager
from management.utils import is_valid_sender_email


class Command(BaseCommand):
    help = 'Create a new management login'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, required=False)
        parser.add_argument('-e', '--email', type=str, required=False)
        parser.add_argument('--send-login-infos', action='store_true', default=False)

    def handle(self, *args, **options):
        username = options['username'] or input('Username: ')  # nosec
        email = options['email'] or input('E-Mail: ')  # nosec

        validate_email(email)
        if not is_valid_sender_email(email):
            self.stdout.write(
                self.style.ERROR(
                    f'Email must end with either of the following: {", ".join([f"@{i}" for i in settings.VALID_MANAGER_EMAIL_DOMAINS])}'))
            return

        if ElectionManager.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR('An election manager with this email already exists'))
            return

        if options['send_login_infos']:
            password = token_hex(12)
        else:
            password = getpass('Password: ')  # nosec
            repeat_password = getpass('Repeat Password: ')  # nosec
            if password != repeat_password:
                self.stdout.write(self.style.ERROR('Passwords do not match'))
                return

        manager = ElectionManager(username=username, email=email)
        manager.set_password(password)

        if options['send_login_infos']:
            send_mail(
                f'Management login for {settings.URL}',
                f'A new management account on {settings.URL} has been created.\n'
                f'You can login under https://{settings.URL}/management '
                f'with the following data:\n\n'
                f'Username: {username}\n'
                f'Password: {password}',
                settings.EMAIL_SENDER,
                [email],
                fail_silently=False,
            )

        manager.save()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created management login with username {username}, email {email}, password: {password}'))
