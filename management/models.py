from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, PermissionsMixin
from django.db import models

from vote.models import Session, Election


class ElectionManager(AbstractBaseUser):
    email = models.EmailField(unique=True)
    sessions = models.ManyToManyField(Session, related_name='managers', blank=True)

    USERNAME_FIELD = 'email'
    is_staff = False
    is_superuser = False

    def __str__(self):
        return f'{self.email}'

    def get_session(self, pk):
        if self.sessions.filter(pk=pk).exists():
            return self.sessions.get(pk=pk)
        return None

    def get_election(self, pk):
        if Election.objects.filter(session__in=self.sessions).filter(pk=pk).exists():
            return Election.objects.filter(session__in=self.sessions).get(pk=pk)
        return None
