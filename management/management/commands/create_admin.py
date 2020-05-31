from secrets import token_hex

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from management.models import ElectionManager


class Command(BaseCommand):
    help = 'Create a new management login'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--email', type=str, required=True)

    def handle(self, *args, **options):
        email = options['email']
        validate_email(email)
        domain = email.split('@')[1]
        if domain not in ['stusta.de', 'stusta.mhn.de', 'stustanet.de', 'stusta.net']:
            raise ValidationError('Email must be a @stusta.de or @stusta.mhn.de email')

        password = token_hex(12)
        manager = ElectionManager(email=email)
        manager.set_password(password)
        send_mail(
            'Wahlleiter Login vote.stustanet.de',
            f'Für dich wurde ein Wahlleiterlogin auf vote.stustanet.de angelegt.\n'
            f'Du kannst dich unter https://vote.stustanet.de/management mit den '
            f'folgenden Daten einloggen:\n\n'
            f'Benutzername: {email}\n'
            f'Passwort: {password}',
            settings.EMAIL_SENDER,
            [email],
            fail_silently=False,
        )
        manager.save()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created management login with email {email}, password: {password}'))
