#!/usr/bin/env python2.7
# -*- encoding: UTF-8 -*-

import sys
import os
import re
import csv
import argparse
from datetime import datetime, date

from django.utils import timezone
from django.db.models import Q

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--syspath', type=str,
                        default='/usr/local/wsgi/memberdatabase/management',
                        help='e.g. /usr/local/wsgi/memberdatabase/management')
    parser.add_argument('-i', '--inhabitants-list', type=str)
    parser.add_argument('-o', '--out-dir', type=str, default='Output dir for csv files')
    args = parser.parse_args()

    sys.path.append(args.syspath)
    # https://django.readthedocs.org/en/latest/topics/settings.html#calling-django-setup-is-required-for-standalone-django-usage
    import django
    django.setup()

    from mdb.models import Member, House

    # read in current inhabitants for each room
    rooms = {}
    room_re = re.compile(r'^(?P<house>\d{3}-\w{2})-(?P<room>\w{2}-\w{2}-\w)')
    with open(args.inhabitants_list) as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            m = room_re.match(row[0])
            if m.group('house') in ('740-17', '740-18', '740-19'):
                room_number = m.group('house') + ' ' + ''.join(m.group('room')[:6] + 'A')
            else:
                room_number = m.group('house') + ' ' + m.group('room')
            rooms[room_number] = row[2]

    for house in House.objects.all():
        members = Member.objects.select_related(
            'stusta_address'
        ).filter(stusta_address__isnull=False).filter(
            stusta_address__house=house,
            external_address__isnull=True,
            isexternal=False,
            membership_status__status_name__in=('mitglied',), # 'ehrenmitglied'),
        ).filter(
            Q(Q(ismissinginaction__isnull=True) | Q(ismissinginaction__gt=timezone.now()))
        ).filter(
            Q(Q(entity__contact_email__isnull=False) | Q(entity__stustanet_email__isnull=False))
        )

        output = []
        for member in members:
            email = member.entity.contact_email if member.entity.contact_email is not None else member.entity.stustanet_email.address()
            app = member.stusta_address.apartment_code
            if app not in rooms or date.today() > datetime.strptime(rooms[app], '%Y-%m-%d').date():
                continue

            output.append(
                [member.membership_number, member.firstname, member.name, member.stusta_address.apartment_code, email]
            )

        with open(os.path.join(args.out_dir, house.house_name + '.csv'), 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'first_name', 'last_name', 'apartment', 'email'])
            for row in output:
                r = [x.encode('utf-8') if isinstance(x, basestring) or isinstance(x, u"".__class__) else str(x).encode(
                    'utf-8') for x in row]
                writer.writerow(r)
            print('Exporting ' + str(len(output)) + " members for house " + house.house_name)


if __name__ == '__main__':
    sys.exit(main())
