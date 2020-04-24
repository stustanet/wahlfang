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
    application_due_date = models.DateTimeField()
    max_votes_yes = models.IntegerField()

    @property
    def closed(self):
        return self.end_date > timezone.now()

    @property
    def is_active(self):
        return self.start_date < timezone.now() < self.end_date

    @property
    def can_vote(self):
        return self.application_due_date < timezone.now() < self.end_date

    @property
    def can_apply(self):
        return self.is_active and timezone.now() < self.application_due_date

    @property
    def applications(self):
        return Application.objects.filter(user__in=self.participants.all())

    def __str__(self):
        return self.title


class User(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voted = models.BooleanField(default=False)
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256)
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='participants', on_delete=models.CASCADE)

    @classmethod
    def user_exists(cls, token):
        try:
            t = uuid.UUID(token, version=4)
        except ValueError:
            return False

        return cls.objects.filter(token=token).exists()

    @property
    def can_vote(self):
        return not self.voted and self.election.can_vote

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Application(models.Model):
    text = models.TextField()
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True, blank=True)
    user = models.OneToOneField(User, related_name='application', on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return f'Application of {self.user} for {self.user.election}'


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Application, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES, max_length=max(len(x[0]) for x in VOTE_CHOICES))
