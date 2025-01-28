from typing import List, TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from ticketing_system.core.exceptions import ApplicationError
from ticketing_system.emails.models import Email
from ticketing_system.emails.services import email_send


if TYPE_CHECKING:
    from pytest_mock import MockerFixture  # For typing the `mocker` fixture
    from django.core.mail import EmailMessage


pytestmark = pytest.mark.django_db


def test_email_send_srvice_return_successful(
        test_email_with_sending_status: 'Email',
        mailoutbox: List['EmailMessage']
) -> None:

    """
    Verify that the email_send service successfully sends an email.

    This test ensures integration with the actual email backend without mocking.
    It verifies that the email is sent, its status is updated to 'SENT',
    and the 'sent' timestamp is recorded.

    Args:
        test_email_with_sending_status (Email): Email instance in 'SENDING' status.
        mailoutbox (List[EmailMessage]): Mailbox fixture to check sent emails.
    """

    # Call the service
    sent_email = email_send(email=test_email_with_sending_status)
    # Verify email status is updated
    assert sent_email.status == Email.Status.SENT
    assert sent_email.sent_at is not None
    assert sent_email.sent_at <= timezone.now()
    assert sent_email.sent_at > timezone.now() - timezone.timedelta(seconds=5)

    # Verify the email was sent
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.subject == test_email_with_sending_status.subject
    assert mail.body == test_email_with_sending_status.message
    assert mail.from_email == test_email_with_sending_status.from_email
    assert mail.to == [test_email_with_sending_status.to_email]


def test_email_send_service_with_mock_email_return_successful(
        test_email_with_sending_status: 'Email'
) -> None:

    """
    Verify that the email_send service updates the status to 'SENT'
    when the email is successfully sent using a mocked send method.

    Args:
        test_email_with_sending_status (Email): Email instance in 'SENDING' status.
    """

    # Mock the actual send call
    with patch.object(EmailMultiAlternatives, 'send', return_value=None):
        sent_email = email_send(email=test_email_with_sending_status)

    assert sent_email.status == Email.Status.SENT
    assert sent_email.sent_at is not None
    assert sent_email.sent_at <= timezone.now()


def test_email_send_service_with_failure_simulation_return_error(
        test_email_with_sending_status: 'Email', mocker: 'MockerFixture'
) -> None:

    """
    Verify that the email_send service raises an ApplicationError and
    sets the email status to 'FAILED' when failure simulation is triggered.

    Args:
        test_email_with_sending_status (Email): Email instance in 'SENDING' status.
    """

    # Mock send failure
    mocker.patch(
        'django.core.mail.EmailMultiAlternatives.send',
        side_effect=Exception("SMTP Error")
    )

    # Test error handling
    with pytest.raises(ApplicationError):
        email_send(test_email_with_sending_status)

        test_email_with_sending_status.refresh_from_db()
        assert test_email_with_sending_status.status == Email.Status.FAILED


def test_email_send_service_with_invalid_status_return_error(
        test_email_with_ready_status: 'Email'
) -> None:

    """
    Verify that the email_send service raises an ApplicationError when the email
    is not in the 'SENDING' status.

    Args:
        test_email_with_ready_status (Email): Email instance not in 'SENDING' status.
    """

    with pytest.raises(
        ApplicationError, match="Cannot send non-sending emails. Current status is READY"
    ):
        email_send(email=test_email_with_ready_status) # Invalid status for sending
