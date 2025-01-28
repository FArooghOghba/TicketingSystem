from datetime import timedelta
import logging
from typing import TypeVar

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from ticketing_system.authentication.token_service import TokenService
from ticketing_system.core.exceptions import ApplicationError
from ticketing_system.core.services import model_update
from ticketing_system.emails.models import Email


logger = logging.getLogger(__name__)

User = TypeVar("User", bound=get_user_model())


def create_email(
    from_email: str, to_email: str, subject: str, message: str, html: str = ""
) -> 'Email':

    """
    Create an email instance and queue it in the 'READY' state.

    Args:
        from_email (str): Sender's email address.
        to_email (str): Recipient's email address.
        subject (str): Subject of the email.
        message (str): Plain-text content of the email.
        html (str, optional): HTML content of the email. Defaults to an empty string.

    Returns:
        Email: The created email instance.
    """

    return Email.objects.create(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        message=message,
        html=html
    )


@transaction.atomic
def email_failed(email: Email) -> Email:

    """
    Mark an email as failed if it's in the 'SENDING' state.

    Args:
        email (Email): The email instance to update.

    Raises:
        ApplicationError: If the email is not in the 'SENDING' state.

    Returns:
        Email: The updated email instance.
    """

    if email.status != Email.Status.SENDING:

        raise ApplicationError(
            f"Cannot fail non-sending emails. Current status is {email.status}"
        )

    email, _ = model_update(
        instance=email, fields=["status"], data={"status": Email.Status.FAILED}
    )
    return email


@transaction.atomic
def email_send(email: 'Email') -> 'Email':

    """
    Send an email and update its status to 'SENT' upon success.

    Args:
        email (Email): The email instance to send.

    Raises:
        ApplicationError: If email sending fails due to failure simulation.

    Returns:
        Email: The updated email instance.
    """

    if email.status != Email.Status.SENDING:
        raise ApplicationError(
            f"Cannot send non-sending emails. Current status is {email.status}"
        )

    # Prepare and send email
    msg = EmailMultiAlternatives(
        subject=email.subject,
        body=email.message,
        from_email=email.from_email,
        to=[email.to_email]
    )

    if email.html:
        msg.attach_alternative(email.html, "text/html")

    try:
        msg.send()
    except Exception:
        email_failed(email=email)  # Update status to FAILED on exception
        raise ApplicationError("Failed to send email.")

    email, _ = model_update(
        instance=email, fields=["status", "sent_at"],
        data={"status": Email.Status.SENT, "sent_at": timezone.now()}
    )
    return email


@transaction.atomic
def send_registration_email(*, user: 'User') -> Email:

    """
    Send a registration confirmation email.

    Args:
        user (User): The recipient user.

    Returns:
        Email: The created and optionally sent email instance.
    """

    subject = settings.DEFAULT_REGISTRATION_EMAIL_SUBJECT
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    # Generate password reset URL with a token
    verification_url = TokenService.generate_url_with_token(
        user=user,
        token_type='access',
        expiry=timedelta(minutes=30),
        view_name='auth:verify-email'
    )

    # Render message content with a template
    message = render_to_string(
        template_name=settings.DEFAULT_REGISTRATION_EMAIL_TEMPLATE_TXT,
        context={'user': user, 'verification_url': verification_url}
    ) or "Verifi your account using this link: {}".format(verification_url)

    html_message = render_to_string(
        template_name=settings.DEFAULT_REGISTRATION_EMAIL_TEMPLATE_HTML,
        context={'user': user, 'verification_url': verification_url}
    )

    # Create the email record
    email = create_email(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        message=message,
        html=html_message
    )


    email, _ = model_update(
        instance=email, fields=["status"], data={"status": Email.Status.SENDING}
    )
    email_send(email)

    logger.info(f"Registration email sent to {email}")
    return email
