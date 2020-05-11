from django.core.management.base import BaseCommand

from vote.email import send_time_correction


class Command(BaseCommand):
    help = 'Notify all voters that signed up for automatic reminder'

    def handle(self, *args, **options):
        send_time_correction()
