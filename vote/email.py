from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from vote.models import Voter


def email_voters(voters, subject, template):
    with mail.get_connection(fail_silently=True) as connection:
        for voter in voters:
            context = {
                'voter': voter,
                'election': voter.election,
            }
            body = render_to_string(template, context=context)

            body_html = body.replace('\n', '<br/>')
            body_plain = strip_tags(body)

            message = EmailMultiAlternatives(
                subject,
                body_plain,
                settings.EMAIL_SENDER,
                [voter.email],
                connection=connection)
            message.attach_alternative(body_html, 'text/html')
            message.send(fail_silently=True)
    print(f'Successfully sent emails to {voters.count()} voters')


def remind_voters():
    voters = Voter.objects.filter(remind_me=True)
    email_voters(
        voters=voters,
        subject='Erinnerung Hausadmin Wahlen | Reminder house admin elections',
        template='vote/mails/reminder.j2'
    )


def send_time_correction():
    voters = Voter.objects.all()
    email_voters(
        voters=voters,
        subject='Korrektur Hausadmin Wahlen | Correction house admin elections',
        template='vote/mails/time_correction.j2'
    )
