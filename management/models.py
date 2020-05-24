from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, PermissionsMixin
from django.db import models

from vote.models import Election


class ElectionManager(AbstractBaseUser):
    email = models.EmailField(unique=True)
    elections = models.ManyToManyField(Election, related_name='managers', blank=True)

    USERNAME_FIELD = 'email'
    is_staff = False
    is_superuser = False

    def __str__(self):
        return f'{self.email}'

    def get_election(self, pk):
        if self.elections.filter(pk=pk).exists():
            return self.elections.get(pk=pk)
        return None
