from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from ticketing_system.authentication.token_service import TokenService
from ticketing_system.core.exceptions import ApplicationError

if TYPE_CHECKING:
    from django.test import Client
    from pytest_mock import MockerFixture  # For typing the `mocker` fixture


pytestmark = pytest.mark.django_db

User = get_user_model()

def user_verification_email_url(user: 'User') -> str:

    """
    Generate a verification email URL for a given user.

    Args:
        user (User): The user for whom the verification URL is generated.

    Returns:
        str: The generated URL containing a JWT token.
    """

    return TokenService.generate_url_with_token(
        user=user,
        token_type='access',
        expiry=settings.DEFAULT_REGISTRATION_EMAIL_JWT_MAX_AGE,
        view_name='auth:verify-email'
    )


def test_get_request_user_verification_email_return_successful(
        client: 'Client', first_test_unverified_user: 'User'
) -> None:

    """
    Test that a GET request to the verification email URL successfully
    verifies a user.

    Steps:
    - Generate a verification URL for an unverified user.
    - Send a GET request to the URL.
    - Check if the response is successful.
    - Ensure the user's `is_verified` attribute is updated to True.
    """

    url = user_verification_email_url(user=first_test_unverified_user)
    response = client.get(path=url)

    first_test_unverified_user.refresh_from_db()
    assert response.status_code == HTTPStatus.OK
    assert "successfully" in response.context["message"]
    assert first_test_unverified_user.is_verified is True


def test_get_request_user_verification_email_already_verified_user(
        client: 'Client', first_test_user: 'User'
) -> None:

    """
    Test that attempting to verify an already verified user returns
    an appropriate message.

    Steps:
    - Generate a verification URL for a user who is already verified.
    - Send a GET request to the URL.
    - Check if the response indicates the user is already verified.
    """

    url = user_verification_email_url(user=first_test_user)
    response = client.get(path=url)

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.context["status"] == "already_verified"
    assert "Your account has already been verified." in response.context["message"]


def test_get_request_user_verification_email_with_expired_token_return_error(
        client: 'Client', first_test_unverified_user: 'User', mocker: 'MockerFixture'
) -> None:

    """
    Test that an expired or invalid token results in an error message.

    Steps:
    - Mock `TokenService.validate_token` to raise an `ApplicationError`
    indicating an expired token.
    - Generate a verification URL.
    - Send a GET request to the URL.
    - Check if the response contains an error message about the expired token.
    """

    # Mock token age validation
    mocker.patch(
        'ticketing_system.authentication.views.TokenService.validate_token',
        side_effect=ApplicationError("Invalid or expired token")
    )

    url = user_verification_email_url(user=first_test_unverified_user)
    response = client.get(path=url)

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.context["status"] == "error"
    assert "expired" in response.context["message"].lower()


def test_get_request_user_verification_email_missing_user_return_error(
        client: 'Client', first_test_unverified_user: 'User', mocker: 'MockerFixture'
) -> None:

    """
    Test that a request with a token for a non-existent user results in an error message.

    Steps:
    - Mock `TokenService.validate_token` to raise a `User.DoesNotExist` exception.
    - Generate a verification URL.
    - Send a GET request to the URL.
    - Check if the response contains an error message indicating the user was not found.
    """

    mocker.patch(
        "ticketing_system.authentication.token_service.TokenService.validate_token",
        side_effect=User.DoesNotExist
    )

    url = user_verification_email_url(user=first_test_unverified_user)
    response = client.get(path=url)

    # Assert
    assert response.status_code == 200
    assert response.context["status"] == "error"
    assert "not found" in response.context["message"].lower()
