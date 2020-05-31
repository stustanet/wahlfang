import os
import sys
import textwrap
import uuid
from io import BytesIO

import PIL
from PIL import Image
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count, Q, CASCADE
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags

VOTE_ACCEPT = 'accept'
VOTE_ABSTENTION = 'abstention'
VOTE_REJECT = 'reject'
VOTE_CHOICES = [
    (VOTE_ABSTENTION, 'Abstention'),
    (VOTE_ACCEPT, 'Yes'),
    (VOTE_REJECT, 'No'),
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
            out = Enc32.alphabet[0] * (length - len(out)) + out
        return out

    @staticmethod
    def decode(s):
        i = 0
        for c in s:
            i <<= 5
            i += Enc32.dec_map[c]
        return i


class Session(models.Model):
    title = models.CharField(max_length=256)
    meeting_link = models.CharField(max_length=512, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True, default=timezone.now)


class Election(models.Model):
    title = models.CharField(max_length=512)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    max_votes_yes = models.IntegerField(blank=True, null=True)
    session = models.ForeignKey(Session, related_name='elections', on_delete=CASCADE)
    result_published = models.CharField(max_length=1, choices=[('0', 'unpublished'), ('1', 'only winners published'),
                                                               ('2', 'fully published')], default='0')

    @property
    def started(self):
        if self.start_date is not None and self.end_date is not None:
            return timezone.now() > self.start_date
        else:
            return False

    @property
    def closed(self):
        if self.end_date:
            return self.end_date < timezone.now()
        else:
            return False

    @property
    def is_open(self):
        if self.end_date:
            return self.start_date < timezone.now() < self.end_date
        else:
            return False

    @property
    def can_apply(self):
        if self.start_date:
            return timezone.now() < self.start_date
        else:
            return True

    @property
    def applications(self):
        return Application.objects.filter(election=self)

    @property
    def election_summary(self):
        if not self.closed:
            return self.objects.none()

        votes_accept = Count('votes', filter=Q(votes__vote=VOTE_ACCEPT))
        votes_reject = Count('votes', filter=Q(votes__vote=VOTE_REJECT))
        votes_abstention = Count('votes', filter=Q(votes__vote=VOTE_ABSTENTION))

        applications = Application.objects.filter(election_id=self.pk).annotate(
            votes_accept=votes_accept,
            votes_reject=votes_reject,
            votes_abstention=votes_abstention
        ).order_by('-votes_accept')

        return applications

    def number_voters(self):
        return self.session.participants.count()

    def number_votes_open(self):
        return self.open_votes.count()

    def number_votes_cast(self):
        if self.applications.count() == 0:
            return 0
        return int(self.votes.count() / self.applications.count())

    def __str__(self):
        return self.title


class Voter(models.Model):
    voter_id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=256)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField()
    session = models.ForeignKey(Session, related_name='participants', on_delete=models.CASCADE)
    remind_me = models.BooleanField(default=False)

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    USERNAME_FIELD = 'voter_id'

    class Meta:
        unique_together = ('session', 'email')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        fields = kwargs.pop('update_fields', [])
        if fields == ['last_login']:
            return
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def set_password(self, raw_password=None):
        if not raw_password:
            raw_password = get_random_string(length=20, allowed_chars=Enc32.alphabet)
        self.password = make_password(raw_password)
        self._password = raw_password
        return raw_password

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
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @property
    def is_active(self):
        return self.has_usable_password()

    def can_vote(self, election):
        return election.is_open and OpenVote.objects.filter(voter_id=self.voter_id, election_id=election.id).exists()

    @property
    def is_staff(self):
        return False

    def has_module_perms(self, app_label):
        return False

    def get_username(self):
        return str(self)

    def send_invitation(self, access_code):
        subject = f'Einladung {self.session.title}'
        context = {
            'voter': self,
            'session': self.session,
            'login_url': 'https://vote.stustanet.de' + reverse('vote:link_login', kwargs={'access_code': access_code}),
            'access_code': access_code,
        }
        body_html = render_to_string('vote/mails/invitation.j2', context=context)

        self.email_user(
            subject=subject,
            message=strip_tags(body_html),
            from_email=self.session.managers.all().first().email,
            html_message=body_html.replace('\n', '<br/>'),
            fail_silently=True
        )

    @staticmethod
    def get_access_code(voter, raw_password):
        if isinstance(voter, Voter):
            voter_id = voter.voter_id
        else:
            voter_id = int(voter)

        enc_id = Enc32.encode(voter_id, 4)
        return '-'.join(textwrap.wrap(enc_id + raw_password, 6))

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
    def from_data(cls, session, email, first_name=None, last_name=None):
        voter = Voter(
            first_name=first_name,
            last_name=last_name,
            session=session,
            email=email,
        )
        password = voter.set_password()
        voter.save()

        return voter, cls.get_access_code(voter.voter_id, password)


def avatar_file_name(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('avatars', str(uuid.uuid4()) + "." + ext)


class Application(models.Model):
    text = models.TextField(max_length=250, blank=True)
    avatar = models.ImageField(upload_to=avatar_file_name, null=True, blank=True)
    election = models.ForeignKey(Election, related_name='application', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=256)
    email = models.EmailField(null=True, blank=True)

    _old_avatar = None

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self._old_avatar = self.avatar

    def __str__(self):
        return f'Application of {self.get_display_name()} for {self.election}'

    def get_display_name(self):
        return f'{self.display_name}'

    def save(self, *args, **kwargs):
        if self.avatar and self._old_avatar != self.avatar:
            # remove old file
            if self._old_avatar and os.path.isfile(self._old_avatar.path):
                # let's not play russian roulette
                path = os.path.normpath(self._old_avatar.path)
                if path.startswith(os.path.join(settings.MEDIA_ROOT, 'avatars')):
                    os.remove(path)

            max_width = 100
            max_height = 100
            img = Image.open(self.avatar)

            # remove alpha channel
            if img.mode in ('RGBA', 'LA'):
                background = Image.new(img.mode[:-1], img.size, '#FFF')
                background.paste(img, img.split()[-1])
                img = background

            # resize
            width = max_width
            width_percent = (width / float(img.size[0]))
            height = int((float(img.size[1]) * float(width_percent)))
            if height > max_height:
                height = max_height
                height_percent = (height / float(img.size[1]))
                width = int((float(img.size[0]) * float(height_percent)))
            img = img.resize((width, height), PIL.Image.ANTIALIAS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            self.avatar = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.avatar.name.split('.')[0],
                                               'image/jpeg', sys.getsizeof(output), None)
            self._old_avatar = self.avatar

        super(Application, self).save(*args, **kwargs)


class OpenVote(models.Model):
    election = models.ForeignKey(Election, related_name='open_votes', on_delete=models.CASCADE)
    voter = models.ForeignKey(Voter, related_name='open_votes', on_delete=models.CASCADE)

    def can_vote(self, voter_id, election_id):
        return self.objects.filter(voter_id=voter_id, election_id=election_id).exists()


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Application, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES, max_length=max(len(x[0]) for x in VOTE_CHOICES))
