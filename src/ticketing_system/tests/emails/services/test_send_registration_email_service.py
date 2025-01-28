from typing import List, TYPE_CHECKING, TypeVar

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ticketing_system.emails.models import Email
from ticketing_system.emails.services import send_registration_email

if TYPE_CHECKING:
    from pytest_mock import MockerFixture  # For typing the `mocker` fixture
    from django.core.mail import EmailMessage


pytestmark = pytest.mark.django_db

User = TypeVar("User", bound=get_user_model())



def test_send_registration_email_return_successful(
        first_test_user: 'User', mocker: 'MockerFixture',
        mailoutbox: List['EmailMessage']
) -> None:

    """
    Test sending a registration email in synchronous mode.

    Verifies that:
    - An email is successfully created and sent.
    - The email contains the correct recipient, status, and content.
    - The reset URL is embedded in the email message.
    """

    # Mock the token generation to return a fixed URL
    mocker.patch(
        "ticketing_system.authentication.token_service.TokenService.generate_url_with_token",
        return_value="https://example.com/reset-password"
    )

    # Call the service
    email = send_registration_email(user=first_test_user)

    # Verify the email was sent
    assert len(mailoutbox) == 1

    # Assert email is created correctly
    assert email.to_email == first_test_user.email
    assert email.status == Email.Status.SENT
    assert email.message is not None
    assert "https://example.com/reset-password" in email.message


def test_send_registration_email_with_invalid_email_return_error(
        first_test_user: 'User'
) -> None:

    """
    Test that the service raises a ValidationError for an invalid email address.

    Ensures that users with improperly formatted email addresses
    cannot trigger the password reset email functionality.
    """

    # Set an invalid email address
    first_test_user.email = "invalid-email"
    first_test_user.save()

    # Verify that a ValidationError is raised
    with pytest.raises(ValidationError, match="Enter a valid email address."):
        send_registration_email(user=first_test_user)

def test_send_registration_email_with_token_generation_failure_return_error(
        first_test_user: 'User', mocker: 'MockerFixture'
) -> None:

    """
    Test that the service handles token generation failure gracefully.

    Ensures that an exception during token generation propagates properly.
    """

    # Mock the token generation to raise an exception
    mocker.patch(
        "ticketing_system.authentication.token_service.TokenService.generate_url_with_token",
        side_effect=Exception("Token generation failed")
    )

    with pytest.raises(Exception, match="Token generation failed"):
        send_registration_email(user=first_test_user)
