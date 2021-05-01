import threading
import time
from typing import List, Tuple

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from management.utils import is_valid_sender_email
from vote.models import Session, Election, Voter


class ElectionManager(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=255)
    email = models.EmailField(null=True, blank=True)
    sessions = models.ManyToManyField(Session, related_name='managers', blank=True)

    USERNAME_FIELD = 'username'
    is_staff = False
    is_superuser = False

    def __str__(self):
        return f'{self.username}'

    @property
    def sender_email(self):
        if self.email and is_valid_sender_email(self.email):
            return self.email

        return settings.EMAIL_SENDER

    def get_session(self, pk):
        return self.sessions.filter(pk=pk).first()

    def get_election(self, pk):
        return Election.objects.filter(session__in=self.sessions).filter(pk=pk).first()

    def send_invite_bulk_threaded(self, voters_codes: List[Tuple[Voter, str]]):
        def runner():
            failed_voters = list(filter(lambda i: i[0] is not None,
                                        (voter.send_invitation(code, self.sender_email) for voter, code in
                                         voters_codes)))

            def wait_heuristic():
                # heuristic sleep to avoid a channel message before the manager's websocket reconnected
                # after x send emails this sleep should be unnecessary
                if len(failed_voters) < 10:
                    time.sleep(1)

            group = "SessionAlert-" + str(voters_codes[0][0].session.pk)
            if len(failed_voters) == 0:
                wait_heuristic()
                # send message that tells the manager that all emails have been sent successfully
                async_to_sync(get_channel_layer().group_send)(
                    group,
                    {'type': 'send_succ', 'msg': "Emails send successfully!"}
                )
                return
            failed_emails_str = "".join(
                [f"<tr><td>{voter.email}</td><td>{e}</td></tr>" for voter, e in failed_voters])

            msg = 'The following email addresses failed to send and thus are probably unassigned addresses. ' \
                  'Please check them again on correctness.<table class="width100"><tr><th>Email</th>' \
                  '<th>Error</th></tr>{}</table>'

            # delete voters where the email could not be sent
            for voter, _ in failed_voters:
                voter.invalid_email = True
                voter.save()  # may trigger a lot of automatic reloads
            wait_heuristic()
            async_to_sync(get_channel_layer().group_send)(
                group,
                {'type': 'send_alert', 'msg': msg.format(failed_emails_str), 'title': 'Error during email sending',
                 'reload': '#voterCard'}
            )

        thread = threading.Thread(
            target=runner,
            args=())
        thread.start()
