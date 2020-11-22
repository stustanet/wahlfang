from django.core.management.base import BaseCommand
from django.utils import timezone

from vote.models import Election


class Command(BaseCommand):
    help = 'Process all elections and send remind emails to the voters when the elction has started'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for election in Election.objects.all():
            if election.start_date is None or election.remind_text_sent or not election.send_emails_on_start or \
                    timezone.now() < election.start_date:
                continue
            election.remind_text_sent = True
            election.save()
            for voter in election.session.participants.all():
                voter.send_reminder(election.session.managers.all().first().sender_email, election)
