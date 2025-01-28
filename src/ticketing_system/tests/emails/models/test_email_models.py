import pytest
from django.core.exceptions import ValidationError

from ticketing_system.emails.models import Email


pytestmark = pytest.mark.django_db


def test_create_email_return_successful() -> None:

    """
    Test creating an Email instance with valid data.

    This test ensures that an Email instance can be
    successfully created with all required fields.
    It also verifies that default values are correctly
    assigned to optional fields.
    """

    # Create an email instance without setting optional fields
    email = Email.objects.create(
        from_email="test@example.com",
        to_email="user@example.com",
        subject="Test Subject",
        message="This is a test message.",
        html="<p>This is a test message.</p>",
    )

    # Assert default values
    assert email.status == Email.Status.READY
    assert email.sent_at is None


def test_create_email_str_representation_return_successful() -> None:

    """
    Test the string representation of an Email instance.

    This test ensures that the `__str__` method of the Email model
    returns the expected format: 'subject (status)'.
    """

    # Create an email instance
    email = Email.objects.create(
        from_email="test@example.com",
        to_email="user@example.com",
        subject="Test Subject",
        message="This is a test message.",
        html="<p>This is a test message.</p>",
        status=Email.Status.SENT,
    )

    # Assert string representation
    assert str(email) == "Test Subject (Sent)"


def test_create_email_with_invalid_status_return_error() -> None:

    """
    Test creating an Email instance with an invalid status.

    This test ensures that attempting to set an invalid status value
    on an Email instance raises a ValidationError.
    """

    # Test invalid status
    email = Email(
        from_email="test@example.com",
        to_email="user@example.com",
        subject="Test Subject",
        message="This is a test message.",
        html="<p>This is a test message.</p>",
    )
    email.status = "INVALID_STATUS"

    with pytest.raises(ValidationError):
        email.full_clean()


def test_create_email_with_invalid_email_format_return_error() -> None:

    """
    Test creating an Email instance with invalid email formats.

    This test ensures that providing invalid email formats for
    `from_email` or `to_email` raises a ValidationError during validation.
    """
    
    # Test invalid from_email
    email = Email(
        from_email="invalid-email",
        to_email="user@example.com",
        subject="Test Subject",
        message="This is a test message.",
        html="<p>This is a test message.</p>",
    )
    with pytest.raises(ValidationError):
        email.full_clean()  # Explicitly trigger validation

    # Test invalid to_email
    email = Email(
        from_email="test@example.com",
        to_email="invalid-email",
        subject="Test Subject",
        message="This is a test message.",
        html="<p>This is a test message.</p>",
    )
    with pytest.raises(ValidationError):
        email.full_clean()  # Explicitly trigger validation