from django.db import models
from django.utils import timezone

import uuid

VOTE_ACCEPT = 'accept'
VOTE_ABSTENTION = 'abstention'
VOTE_REJECT = 'reject'
VOTE_CHOICES = [
    (VOTE_ACCEPT, 'für'),
    (VOTE_REJECT, 'gegen'),
    (VOTE_ABSTENTION, 'Enthaltung'),
]


class Election(models.Model):
    title = models.CharField(max_length=512)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @property
    def applications(self):
        return Application.objects.filter(user__in=self.participants.all())


class User(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voted = models.BooleanField(default=False)
    # ip = models.CharField()  # TODO
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256)
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='participants', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def can_vote(self):
        return not self.voted and self.election.start_date < timezone.now() < self.election.end_date


class Application(models.Model):
    text = models.TextField()
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True, blank=True)
    user = models.OneToOneField(User, related_name='application', on_delete=models.CASCADE)

    def __str__(self):
        return f'Application of {self.user}'


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Application, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES, max_length=max(len(x[0]) for x in VOTE_CHOICES))
