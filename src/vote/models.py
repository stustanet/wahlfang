from django.db import models
from django.utils import timezone

import uuid

VOTE_ACCEPT = 'accept'
VOTE_ABSTENTION = 'abstention'
VOTE_REJECT = 'reject'
VOTE_CHOICES = [VOTE_ACCEPT, VOTE_ABSTENTION, VOTE_REJECT]


class Election(models.Model):
    title = models.CharField(max_length=512)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Token(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    used = models.BooleanField(default=False)
    ip = models.CharField()  # TODO
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='tokens', on_delete=models.CASCADE)

    def __str__(self):
        return f'Token'

    @property
    def valid(self):
        return not self.used and self.election.end_date < timezone.now()


class Candidate(models.Model):
    lastname = models.CharField(max_length=256)
    firstname = models.CharField(max_length=256)
    application = models.TextField()
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True)
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='candidates', on_delete=models.CASCADE)

    def __str__(self):
        return f'Candidate {self.firstname} {self.lastname}'


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES)
