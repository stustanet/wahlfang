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
    # ip = models.CharField()  # TODO
    # last_name = models.CharField(max_length=256)
    # first_name = models.CharField(max_length=256)
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='tokens', on_delete=models.CASCADE)

    def __str__(self):
        return f'Token of {self.email}'

    @property
    def valid(self):
        return not self.used and self.election.end_date < timezone.now()


class Candidate(models.Model):
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256)
    application = models.TextField()
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True)
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='candidates', on_delete=models.CASCADE)

    def __str__(self):
        return f'Candidate {self.first_name} {self.last_name}'


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=[(x, x) for x in VOTE_CHOICES], max_length=max(len(x) for x in VOTE_CHOICES))
