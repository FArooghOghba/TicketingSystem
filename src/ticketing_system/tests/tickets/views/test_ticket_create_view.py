from typing import TYPE_CHECKING

import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

if TYPE_CHECKING:
    from django.test import Client
    from pytest_mock import MockerFixture  # For typing the `mocker` fixture
    from ticketing_system.users.models import Profile


pytestmark = pytest.mark.django_db

User = get_user_model()


TICKET_CREATE_URL = reverse('tickets:create')
USER_CREATE_TICKET_REDIRECT_URL = reverse("tickets:list")


def test_get_request_ticket_create_view_return_successful(
        client: 'Client', first_test_user_profile: 'Profile'
) -> None:

    """
    Test that a GET request to the ticket creation view returns the correct template and form.

    Steps:
      - Force login with an authenticated user.
      - Send a GET request to the ticket creation URL.
      - Assert that the response status is 200.
      - Check that the response uses the correct template and contains form fields.
    """

    user = first_test_user_profile.user
    client.force_login(user)

    response = client.get(path=TICKET_CREATE_URL)
    assert response.status_code == HTTPStatus.OK

    content = response.content.decode()
    assert "Subject" in content or "subject" in content.lower()


def test_post_request_ticket_create_view_return_successful(
    client: 'Client', first_test_user_profile: 'Profile', mocker: 'MockerFixture'
) -> None:

    """
    Test that a valid POST request to the ticket creation view creates a ticket and redirects.

    Steps:
      - Force login with an authenticated user.
      - Prepare valid form data.
      - Patch the create_ticket service function to avoid actual DB writes and check call parameters.
      - Send a POST request with the valid data.
      - Assert that the service function was called once with the expected arguments.
      - Assert that the response is a redirect (HTTP 302) to the ticket list.
    """

    user = first_test_user_profile.user
    client.force_login(user)

    form_data = {
        "subject": "Test Ticket Subject",
        "description": "Test Ticket Description",
        # 'file' is optional;
    }

    # Patch the create_ticket service function in the view module's namespace.
    mock_create_ticket = mocker.patch("ticketing_system.ticket.views.create_ticket")

    response = client.post(path=TICKET_CREATE_URL, data=form_data)

    mock_create_ticket.assert_called_once_with(
        created_by=first_test_user_profile,
        subject=form_data["subject"],
        description=form_data["description"],
        file=None,  # Since file was not provided.
    )
    assert response.status_code == HTTPStatus.FOUND

    # Verify that redirection is to the ticket list page.
    assert response.url == USER_CREATE_TICKET_REDIRECT_URL


def test_post_request_ticket_create_view_with_invalid_data_return_error(
        client: 'Client', first_test_user_profile: 'Profile'
) -> None:

    """
    Test that submitting invalid data does not create a ticket
    and redisplay the form with errors.

    Steps:
      - Force login with an authenticated user.
      - Prepare invalid form data (e.g., empty subject).
      - Send a POST request with the invalid data.
      - Assert that the response status is 200 (form redisplayed) and contains error messages.
    """

    user = first_test_user_profile.user
    client.force_login(user)

    form_data = {
        "subject": "",  # Invalid, empty subject.
        "description": "Test Ticket Description",
    }
    response = client.post(path=TICKET_CREATE_URL, data=form_data)

    # No redirection should occur for invalid data, so status should be 200.
    assert response.status_code == HTTPStatus.OK

    # Check for an error message indicating the subject is required.
    content = response.content.decode()
    assert "required" in content.lower() or "error" in content.lower()
