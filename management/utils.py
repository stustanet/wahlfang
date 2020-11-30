from django.conf import settings


def is_valid_sender_email(email: str) -> bool:
    if not isinstance(email, str) or '@' not in email:
        return False

    return email.split('@')[-1] in settings.VALID_MANAGER_EMAIL_DOMAINS
