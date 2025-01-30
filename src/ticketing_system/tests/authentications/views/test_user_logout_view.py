from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse


if TYPE_CHECKING:
    from django.test import Client


pytestmark = pytest.mark.django_db


USER_LOGIN_URL = reverse('auth:login')
USER_LOGOUT_URL = reverse('auth:logout')
User = get_user_model()


def test_get_request_user_logout_view_redirect_successful(
        client: 'Client', first_test_user: 'User'
) -> None:

    """
    Test that when an authenticated user accesses the logout view,
    they are successfully logged out and redirected to the login page.
    """

    client.force_login(user=first_test_user)
    response = client.get(path=USER_LOGOUT_URL)

    # 302 Redirect
    assert response.status_code == HTTPStatus.FOUND

    # Redirects to log in
    assert response.url == USER_LOGIN_URL


def test_get_request_user_logout_view_message_return_successful(
        client: 'Client', first_test_user: 'User'
) -> None:

    """
    Test that logging out:
    - Redirects the user to the login page
    - Clears the authenticated session
    - Displays a logout success message
    """

    client.force_login(user=first_test_user)

    response = client.get(path=USER_LOGOUT_URL, follow=True)
    messages = list(get_messages(response.wsgi_request))

    # Final response should be 200 after redirection
    assert response.status_code == HTTPStatus.OK

    # User is redirected to log in
    assert response.redirect_chain[-1][0] == USER_LOGIN_URL

    # User session should be cleared
    assert not response.wsgi_request.user.is_authenticated
    assert str(messages[0]) == "You have been logged out successfully."
