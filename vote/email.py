from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
