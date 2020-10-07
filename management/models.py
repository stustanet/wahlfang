from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, PermissionsMixin
from django.db import models

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
    def stusta_email(self):
        if self.email and self.email.split('@')[-1] in settings.VALID_STUSTA_EMAIL_SUFFIXES:
            return self.email

        return f'{self.username}@stusta.de'

    def get_session(self, pk):
        return self.sessions.filter(pk=pk).first()

    def get_election(self, pk):
        return Election.objects.filter(session__in=self.sessions).filter(pk=pk).first()
