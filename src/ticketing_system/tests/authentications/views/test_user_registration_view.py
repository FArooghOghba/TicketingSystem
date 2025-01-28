from http import HTTPStatus
from typing import Dict, TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from ticketing_system.authentication.forms import CustomUserCreationForm

if TYPE_CHECKING:
    from django.test import Client
    from pytest_mock import MockerFixture  # For typing the `mocker` fixture


pytestmark = pytest.mark.django_db

USER_REGISTER_URL = reverse('auth:register')
USER_LOGIN_URL = reverse('auth:login')
User = get_user_model()


def test_get_request_registration_view_return_successful(
        client: 'Client'
) -> None:

    """
    Test that a GET request to the registration view returns
    a successful response (200 OK), includes a valid form in
    the context, and contains the expected fields.

    Args:
        client (Client): Django test client for making requests.
    """

    response = client.get(path=USER_REGISTER_URL)
    assert response.status_code == HTTPStatus.OK

    # Assert the form is present in the response context and is of the correct type
    assert 'form' in response.context
    assert isinstance(response.context['form'], CustomUserCreationForm)

    # Assert that the form contains the expected fields
    assert 'email' in response.context['form'].fields
    assert 'username' in response.context['form'].fields
    assert 'password1' in response.context['form'].fields
    assert 'password2' not in response.context['form'].fields


def test_post_request_registration_view_with_valid_data_return_successful(
        client: 'Client', first_test_user_payload: Dict[str, str],
        mocker: 'MockerFixture'
) -> None:

    """
    Test that a POST request with valid data to the registration
    view successfully registers a user, redirects to the login page,
    and sends a registration email.

    Args:
        client (Client): Django test client for making requests.
        first_test_user_payload (dict): A valid payload for creating a new user.
        mocker (MockerFixture): Pytest mocker fixture for mocking dependencies.
    """

    mock_send_email = mocker.patch(
        'ticketing_system.authentication.views.send_registration_email'
    )

    response = client.post(
        path=USER_REGISTER_URL,
        data=first_test_user_payload
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == USER_LOGIN_URL

    test_user = User.objects.get(email=first_test_user_payload['email'])

    # Assert the user was created with the correct data
    assert test_user.username == first_test_user_payload['username']
    assert test_user.check_password(first_test_user_payload['password1'])
    assert not test_user.is_verified

    # Assert the registration email was sent
    mock_send_email.assert_called_once_with(user=test_user)


def test_post_request_registration_view_with_invalid_data_return_error(
        client: 'Client', first_test_user_payload: Dict[str, str]
) -> None:

    """
    Test that a POST request with invalid data to the registration
    view returns an error and displays the appropriate validation message.

    Args:
        client (Client): Django test client for making requests.
        first_test_user_payload (dict): A payload for creating a user,
        with missing or invalid fields.
    """

    first_test_user_payload.pop('email')

    response = client.post(
        path=USER_REGISTER_URL,
        data=first_test_user_payload
    )

    assert response.status_code == HTTPStatus.OK

    # Assert the form is present in the response context
    assert 'form' in response.context

    # Assert the response contains the appropriate error message
    assert 'This field is required.' in str(response.content)
