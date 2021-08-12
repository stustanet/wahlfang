from django.db.models import Q
from django.utils import timezone

from vote.models import Election, Session


def upcoming_elections(session: Session):
    return Election.objects.filter(session=session).filter(
        Q(start_date__gt=timezone.now()) | Q(start_date__isnull=True)
    ).order_by('start_date')


def open_elections(session: Session):
    return Election.objects.filter(session=session).filter(
        Q(start_date__isnull=False, end_date__isnull=False, start_date__lte=timezone.now(), end_date__gt=timezone.now())
        | Q(start_date__isnull=False, end_date__isnull=True, start_date__lte=timezone.now())
    ).order_by('-start_date')


def _closed_elections(session: Session):
    return Election.objects.filter(session=session).filter(
        Q(end_date__lte=timezone.now(), end_date__isnull=False)
    ).order_by('-start_date')


def published_elections(session: Session):
    return _closed_elections(session).filter(result_published=True)


def closed_elections(session: Session):
    return _closed_elections(session).filter(result_published=False)
