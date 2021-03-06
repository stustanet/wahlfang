from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from management.utils import is_valid_sender_email
from vote.models import Session, Election


class ElectionManager(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=255)
    email = models.EmailField(null=True, blank=True)
    sessions = models.ManyToManyField(Session, related_name='managers', blank=True)

    USERNAME_FIELD = 'username'
    is_staff = False
    is_superuser = False

    def __str__(self):
        return f'{self.username}'

    @property
    def sender_email(self):
        if self.email and is_valid_sender_email(self.email):
            return self.email

        return settings.EMAIL_SENDER

    def get_session(self, pk):
        return self.sessions.filter(pk=pk).first()

    def get_election(self, pk):
        return Election.objects.filter(session__in=self.sessions).filter(pk=pk).first()
