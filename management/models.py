from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, PermissionsMixin
from django.db import models

from vote.models import Session


class ElectionManager(AbstractBaseUser):
    email = models.EmailField(unique=True)
    sessions = models.ManyToManyField(Session, related_name='managers', blank=True)

    USERNAME_FIELD = 'email'
    is_staff = False
    is_superuser = False

    def __str__(self):
        return f'{self.email}'

