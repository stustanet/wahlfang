import os
import sys
import textwrap
import uuid
from argparse import Namespace
from datetime import datetime
from functools import partial
from io import BytesIO
from typing import Tuple, Optional

import PIL
from PIL import Image
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
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

VOTE_CHOICES_NO_ABSTENTION = [
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
    start_date = models.DateTimeField(blank=True, null=True)
    invite_text = models.TextField(max_length=8000, blank=True, null=True)
    spectator_token = models.UUIDField(unique=True, null=True, blank=True)

    def create_spectator_token(self):
        myid = uuid.uuid4()
        while Session.objects.filter(spectator_token=myid).exists():
            myid = uuid.uuid4()
        self.spectator_token = myid
        self.save()
        return myid


class Election(models.Model):
    title = models.CharField(max_length=512)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    max_votes_yes = models.IntegerField(blank=True, null=True)
    session = models.ForeignKey(Session, related_name='elections', on_delete=CASCADE)
    result_published = models.CharField(max_length=1, choices=[('0', 'unpublished'), ('1', 'published')],
                                        default='0')
    disable_abstention = models.BooleanField(default=False)
    voters_self_apply = models.BooleanField(default=False)
    send_emails_on_start = models.BooleanField(default=False)
    remind_text = models.TextField(max_length=8000, blank=True, null=True)
    remind_text_sent = models.BooleanField(default=False)

    @property
    def started(self):
        if self.start_date is not None:
            return timezone.now() > self.start_date

        return False

    @property
    def closed(self):
        if self.end_date:
            return self.end_date < timezone.now()

        return False

    @property
    def is_open(self):
        if self.start_date and self.end_date:
            return self.start_date < timezone.now() < self.end_date

        if self.start_date:
            return self.start_date < timezone.now()

        return False

    @property
    def can_apply(self):
        if self.start_date:
            return timezone.now() < self.start_date

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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # notify users to reload their page
        group = "Session-" + str(self.session.pk)
        async_to_sync(get_channel_layer().group_send)(
            group,
            {'type': 'send_reload', 'id': '#electionCard'}
        )

    def __str__(self):
        return self.title


class Voter(models.Model):
    voter_id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(null=True, blank=True)
    invalid_email = models.BooleanField(default=False)
    session = models.ForeignKey(Session, related_name='participants', on_delete=models.CASCADE)
    logged_in = models.BooleanField(default=False)
    name = models.CharField(max_length=256, blank=True, null=True)

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    USERNAME_FIELD = 'voter_id'

    class Meta:
        unique_together = ('session', 'email')

    def __str__(self):
        if self.email is None:
            return f'anonymous-{self.pk}'

        return self.email

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if update_fields == ['last_login']:
            return

        super().save(force_insert, force_update, using, update_fields)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None
        # notify manager to reload their page, if the user logged in
        group = "Login-Session-" + str(self.session.pk)
        async_to_sync(get_channel_layer().group_send)(
            group,
            {'type': 'send_reload', 'id': '#voterCard'}
        )

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
            self.save(update_fields=['password'])

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

    def email_user(self, subject, message, from_email=None, **kwargs) -> Tuple[Optional['Voter'], Optional[str]]:
        """Send an email to this user."""
        if self.email is not None:
            try:
                send_mail(subject, message, from_email, [self.email], **kwargs)
            except Exception as e:  # pylint: disable=W0703
                return self, str(e)
        # None means everything is ok
        return None, None

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

    @property
    def is_anonymous(self):
        return self.email is None

    def has_module_perms(self, app_label):
        return False

    def get_username(self):
        return str(self)

    @staticmethod
    def send_test_invitation(title: str, invite_text: str, start_date: datetime, meeting_link: str, to_email: str,
                             from_email: str):
        test_session = Namespace(**{
            "title": title,
            "invite_text": invite_text,
            "start_date": start_date,
            'meeting_link': meeting_link,
        })

        test_voter = Namespace(**{
            "name": "Testname",
            "email": to_email,
            "session": test_session,
        })
        test_voter.email_user = partial(Voter.email_user, test_voter)

        Voter.send_invitation(test_voter, "mock-up-access-token", from_email)

    def send_invitation(self, access_code: str, from_email: str) -> Tuple[Optional['Voter'], Optional[str]]:
        if not self.email:
            return None, None
        subject = f'Invitation for {self.session.title}'
        if self.session.invite_text:
            if self.session.start_date:
                # cast to correct time zone
                current_tz = timezone.get_current_timezone()
                st = current_tz.normalize(self.session.start_date)
            context = {
                'name': self.name,
                'title': self.session.title,
                'access_code': access_code,
                'login_url': f'https://{settings.URL}' + reverse('vote:link_login',
                                                                 kwargs={'access_code': access_code}),
                'start_date': st.strftime("%d.%m.%Y") if self.session.start_date else "",
                'start_time': st.strftime("%H:%M") if self.session.start_date else "",
                'start_date_en': st.strftime("%Y/%m/%d") if self.session.start_date else "",
                'start_time_en': st.strftime("%I:%M %p") if self.session.start_date else "",
                'base_url': f'https://{settings.URL}',
                'meeting_link': self.session.meeting_link
            }
            body_html = self.session.invite_text.format(**context)
        else:
            context = {
                'voter': self,
                'session': self.session,
                'base_url': f'https://{settings.URL}',
                'login_url': f'https://{settings.URL}' + reverse('vote:link_login',
                                                                 kwargs={'access_code': access_code}),
                'access_code': access_code,
            }
            body_html = render_to_string('vote/mails/invitation.j2', context=context)

        return self.email_user(
            subject=subject,
            message=strip_tags(body_html),
            from_email=from_email,
            html_message=body_html.replace('\n', '<br/>'),
            fail_silently=False
        )

    def send_reminder(self, from_email: str, election):
        if not self.email:
            return
        subject = f'{election.title} is now open'
        if election.remind_text:
            if election.end_date:
                # cast to correct time zone
                current_tz = timezone.get_current_timezone()
                et = current_tz.normalize(election.end_date)
            context = {
                'name': self.name,
                'title': election.title,
                'url': f'https://{settings.URL}' + reverse('vote:vote', kwargs={'election_id': election.pk}),
                'end_date': et.strftime("%d.%m.%y") if election.end_date else "",
                'end_time': et.strftime("%H:%M") if election.end_date else "",
                'end_date_en': et.strftime("%Y/%m/%d") if election.end_date else "",
                'end_time_en': et.strftime("%I:%M %p") if election.end_date else "",
            }
            body_html = election.remind_text.format(**context)
        else:
            context = {
                'voter': self,
                'election': election,
                'url': f'https://{settings.URL}' + reverse('vote:vote', kwargs={'election_id': election.pk}),
            }
            body_html = render_to_string('vote/mails/start.j2', context=context)

        self.email_user(
            subject=subject,
            message=strip_tags(body_html),
            from_email=from_email,
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
    def from_data(cls, session, email=None, name=None) -> Tuple['Voter', str]:
        voter = Voter(
            session=session,
            email=email,
            name=name,
        )
        password = voter.set_password()
        voter.save()

        # add open elections from the session where the user was added
        open_votes = [OpenVote(election=election, voter=voter) for election in session.elections.all()
                      if not election.closed]
        OpenVote.objects.bulk_create(open_votes)

        return voter, cls.get_access_code(voter.voter_id, password)

    def new_access_token(self):
        password = self.set_password()
        self.logged_in = False
        self.save()
        return self.get_access_code(self, password)


def avatar_file_name(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('avatars', str(uuid.uuid4()) + '.' + ext)


class Application(models.Model):
    text = models.TextField(max_length=250, blank=True)
    avatar = models.ImageField(upload_to=avatar_file_name, null=True, blank=True)
    election = models.ForeignKey(Election, related_name='application', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=256)
    email = models.EmailField(null=True, blank=True)
    voter = models.ForeignKey(Voter, related_name="application", null=True, blank=True, on_delete=models.CASCADE)

    _old_avatar = None

    class Meta:
        unique_together = ('voter', 'election')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_avatar = self.avatar

    def __str__(self):
        return f'Application of {self.get_display_name()} for {self.election}'

    def get_display_name(self):
        return f'{self.display_name}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
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
            self.avatar = InMemoryUploadedFile(output, 'ImageField', '%s.jpg' % self.avatar.name.split('.')[0],
                                               'image/jpeg', sys.getsizeof(output), None)
            self._old_avatar = self.avatar

        super().save(force_insert, force_update, using, update_fields)


class OpenVote(models.Model):
    election = models.ForeignKey(Election, related_name='open_votes', on_delete=models.CASCADE)
    voter = models.ForeignKey(Voter, related_name='open_votes', on_delete=models.CASCADE)

    def can_vote(self, voter_id, election_id):
        return self.objects.filter(voter_id=voter_id, election_id=election_id).exists()


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Application, related_name='votes', on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES, max_length=max(len(x[0]) for x in VOTE_CHOICES))
    # save method is not called on bulk_create in forms.VoteForm.
    # The model update listener for websockets is implemented in the form.
