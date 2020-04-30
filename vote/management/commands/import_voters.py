import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from vote.models import Election, Voter


class Command(BaseCommand):
    help = 'Imports voters from a csv'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--election-id', type=int, required=True)
        parser.add_argument('-c', '--csv', type=str, required=True)

    def handle(self, *args, **options):
        f = Path(options['csv'])
        if not f.exists():
            self.stdout.write(self.style.ERROR(f'Input file {f} does not exist.'))
            return

        election = Election.objects.get(pk=options['election_id'])

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
                voter.send_invitation(access_code)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(election.participants.all())} voters'))
