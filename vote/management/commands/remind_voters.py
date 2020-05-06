from django.core.management.base import BaseCommand

from vote.email import remind_voters


class Command(BaseCommand):
    help = 'Notify all voters that signed up for automatic reminder'

    def handle(self, *args, **options):
        remind_voters()
