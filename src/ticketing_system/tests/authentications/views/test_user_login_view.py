from http import HTTPStatus
from typing import Dict, TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from ticketing_system.authentication.forms import CustomAuthenticationForm

if TYPE_CHECKING:
    from django.test import Client


pytestmark = pytest.mark.django_db


USER_LOGIN_URL = reverse('auth:login')
USER_LOGIN_REDIRECT_URL = reverse("tickets:list")
User = get_user_model()


def test_get_request_user_login_return_successful(client: 'Client') -> None:

    """
    Verify that the login page is accessible to unauthenticated users.

    This test ensures that an unauthenticated user can access the login page
    and that the expected authentication form is present in the response context.
    """

    response = client.get(path=USER_LOGIN_URL)

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context["form"], CustomAuthenticationForm)


def test_post_request_user_login_redirects_to_success_url(
        client: 'Client', first_test_user_login_payload: Dict[str, str]
) -> None:

    """
    Ensure a successful login redirects the user to the designated success URL.

    Given valid login credentials, the user should be redirected to the
    authenticated user dashboard or task list after login.
    """

    response = client.post(
        path=USER_LOGIN_URL,
        data=first_test_user_login_payload,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == USER_LOGIN_REDIRECT_URL


def test_post_request_user_login_return_success(
        client: 'Client', first_test_user_login_payload: Dict[str, str]
) -> None:

    """
    Verify that a verified user can log in successfully.

    The test checks if a verified user, upon entering correct credentials,
    is authenticated and redirected to the appropriate success page.
    """

    response = client.post(
        path=USER_LOGIN_URL,
        data=first_test_user_login_payload,
        follow=True
    )

    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.user.is_authenticated
    assert response.redirect_chain

    success_message = "Logged in successfully"
    assert success_message in str([m.message for m in get_messages(response.wsgi_request)])


def test_post_request_user_login_unverified_user_redirects_to_verification(
        client, first_test_unverified_user_login_payload: Dict[str, str]
) -> None:

    """
    Ensure that an unverified user is prevented from logging in.

    The test checks if an unverified user attempting to log in is redirected
    to the verification resend page and receives an appropriate verification message.
    """

    response = client.post(
        path=USER_LOGIN_URL,
        data=first_test_unverified_user_login_payload,
        follow=True
    )

    assert response.status_code == HTTPStatus.OK
    assert not response.wsgi_request.user.is_authenticated

    # Checking for the message from `form_valid`
    assert "verify" in response.content.decode()


def test_post_request_user_login_nonactive_user_redirects_to_verification(
        client, first_test_nonactive_user_login_payload: Dict[str, str]
) -> None:

    """
    Ensure that a non-active user cannot log in.

    The test verifies that if a user account is inactive (e.g., banned, suspended),
    they are prevented from logging in and do not gain authentication.
    """

    response = client.post(
        path=USER_LOGIN_URL,
        data=first_test_nonactive_user_login_payload,
        follow=True
    )

    assert response.status_code == HTTPStatus.OK
    assert not response.wsgi_request.user.is_authenticated


def test_post_request_user_login_with_invalid_credentials_return_error(
        client: 'Client', first_test_user_login_payload: Dict[str, str]
) -> None:

    """
    Ensure login fails when incorrect credentials are provided.

    This test modifies the login payload to use an invalid email
    and verifies that authentication fails with an appropriate error message.
    """

    first_test_user_login_payload['email'] = 'invalid@email.com'

    response = client.post(
        path=USER_LOGIN_URL,
        data=first_test_user_login_payload,
        follow=True
    )

    assert response.status_code == HTTPStatus.OK
    assert not response.wsgi_request.user.is_authenticated
    assert "Please enter a correct email address and password." in response.content.decode()
