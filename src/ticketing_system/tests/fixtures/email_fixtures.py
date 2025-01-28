import pytest

from ticketing_system.emails.models import Email
from ticketing_system.tests.factories.email_factories import EmailFactory


@pytest.fixture
def test_email_with_sending_status() -> 'Email':

    """
    Fixture for creating a test Email instance.

    This fixture uses the `EmailFactory` factory
    to create a test email instance. The created email
    can be used in tests to simulate a email with predefined
    attributes for testing various scenarios.

    :return: a test email instance
    """

    return EmailFactory(status=Email.Status.SENDING)


@pytest.fixture
def test_email_with_ready_status() -> 'Email':

    """
    Fixture for creating a test Email instance.
    """

    return EmailFactory()
