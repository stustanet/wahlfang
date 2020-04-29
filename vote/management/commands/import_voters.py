import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from vote.models import Election, Voter


class Command(BaseCommand):
    help = 'Imports voters from a csv'

    def add_arguments(self, parser):
        parser.add_argument('--election-title', type=str, required=True)
        parser.add_argument('--start-date', type=str, required=True)
        parser.add_argument('--application-due-date', type=str, required=True)
        parser.add_argument('--end-date', type=str, required=True)
        parser.add_argument('--max-votes-yes', type=int, required=True)
        parser.add_argument('--csv', type=str, required=True)
        parser.add_argument('--jitsi-link', type=str, required=True)

    def handle(self, *args, **options):
        f = Path(options['csv'])
        if not f.exists():
            self.stdout.write(self.style.ERROR(f'Input file {f} does not exist.'))
            return

        election = Election.objects.get_or_create(
            title=options['election_title'],
            start_date=options['start_date'],
            end_date=options['end_date'],
            max_votes_yes=options['max_votes_yes'],
            application_due_date=options['application_due_date'],
        )[0]

        with f.open('r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            next(reader)  # skip csv header line

            for row in reader:
                # row: id, first_name, last_name, room, email
                room = ''.join(row[3].split(' ')[1].split('-')[:2])  # xxx-xx (xx-xx)-x
                voter, access_code = Voter.from_data(
                    voter_id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    room=room,
                    email=row[4],
                    election=election,
                )
                voter.send_invitation(access_code, conference_link=options['jitsi_link'])

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(election.participants.all())} voters'))
