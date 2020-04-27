import string
import textwrap

from django.conf import settings
from django.db import models
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


VOTE_ACCEPT = 'accept'
VOTE_ABSTENTION = 'abstention'
VOTE_REJECT = 'reject'
VOTE_CHOICES = [
    (VOTE_ACCEPT, 'für'),
    (VOTE_REJECT, 'gegen'),
    (VOTE_ABSTENTION, 'Enthaltung'),
]

class Enc32:
    alphabet = "0123456789abcdefghjknpqrstuvwxyz"
    dec_map = {}
    for index, c in enumerate(alphabet):
        dec_map[c] = index
    dec_map['o'] = dec_map['0']
    dec_map['l'] = dec_map['1']
    dec_map['i'] = dec_map['1']
    dec_map['m'] = dec_map['n']

    @staticmethod
    def encode(i, length=None):
        i = int(i)
        out = ""
        while i > 0:
            idx = i & 0x1f
            out = Enc32.alphabet[idx] + out
            i >>= 5
        if length:
            if len(out) > length:
                raise ValueError("value too large for given length")
            out = Enc32.alphabet[0] * (length-len(out)) + out
        return out

    @staticmethod
    def decode(s):
        i = 0
        for c in s:
            i <<= 5
            i += Enc32.dec_map[c]
        return i

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
        return Application.objects.filter(voter__in=self.participants.all())

    def __str__(self):
        return self.title


class Voter(models.Model):
    voter_id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    room = models.CharField(max_length=64)
    email = models.EmailField()
    election = models.ForeignKey(Election, related_name='participants', on_delete=models.CASCADE)
    voted = models.BooleanField(default=False)

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    USERNAME_FIELD = 'voter_id'

    def __str__(self):
        # return f'{self.first_name} {self.last_name}'
        return '{:06d}'.format(self.voter_id)

    def save(self, *args, **kwargs):
        fields = kwargs.pop('update_fields', [])
        if fields == ['last_login']:
            return
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    def clean(self):
        setattr(self, self.email, self.normalize_email(self.email))

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name + '@' + domain_part.lower()
        return email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def can_vote(self):
        return not self.voted and self.election.can_vote

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @property
    def is_active(self):
        return True

    def has_module_perms(self, app_label):
        return False

    def get_username(self):
        return str(self)

    def send_invitation(self, access_code):
        subject = 'Election invitaion blub blub'
        context = {
            'voter': self,
            'election': self.election,
            'access_code': access_code
        }
        body = render_to_string('vote/mails/invitation.j2', context=context)

        self.email_user(
            subject=subject,
            message=body,
            from_email=settings.EMAIL_SENDER
        )

    @staticmethod
    def get_access_code(voter, raw_password):
        if isinstance(voter, Voter):
            voter_id = voter.voter_id
        else:
            voter_id = int(voter)

        enc_id = Enc32.encode(voter_id, 4)
        return '-'.join(textwrap.wrap(enc_id+raw_password, 6))

    @staticmethod
    def split_access_code(access_code=None):
        if not access_code:
            return None, None

        access_code = access_code.replace('-', '')
        if len(access_code) < 5 or not all(c in Enc32.alphabet for c in access_code):
            return None, None

        voter_id = Enc32.decode(access_code[:4])
        password = access_code[4:].lower()
        return voter_id, password

    @classmethod
    def from_data(cls, voter_id, first_name, last_name, election, email):
        password = get_random_string(length=20, allowed_chars=Enc32.alphabet)
        voter = Voter.objects.create(
            voter_id=voter_id,
            first_name=first_name,
            last_name=last_name,
            election=election,
            email=email,
        )
        voter.set_password(password)

        return voter, cls.get_access_code(voter_id, password)


class Application(models.Model):
    text = models.TextField()
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True, blank=True)
    voter = models.OneToOneField(Voter, related_name='application', on_delete=models.CASCADE)
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256)
    email = models.EmailField()

    def __str__(self):
        return f'Application of {self.voter} for {self.voter.election}'


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Application, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES, max_length=max(len(x[0]) for x in VOTE_CHOICES))
