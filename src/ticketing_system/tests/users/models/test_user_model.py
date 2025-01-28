"""
Tests for User Model.
"""

import pytest
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


def test_create_user_with_email_return_successful() -> None:

    """
    Test creating a user with an email is successful.
    :return: None
    """

    email = 'test@example.com'
    username = 'test_user'
    password = 'test_pass123'
    test_user = get_user_model().objects.create_user(
        email=email,
        username=username,
        password=password
    )

    assert test_user.email == email
    assert test_user.is_staff is False
    assert test_user.check_password(password) is True


@pytest.mark.parametrize(
    'email, username, email_expected_format',
    [
        ('test1@EXAMPLE.com', 'test_username1', 'test1@example.com'),
        ('Test2@Example.com', 'test_username2', 'test2@example.com'),
        ('TEST3@EXAMPLE.com', 'test_username3', 'test3@example.com'),
        ('test4@example.COM', 'test_username4', 'test4@example.com'),
    ],
)
def test_new_user_email_normalized_return_successful(
        email: str, username: str, email_expected_format: str
) -> None:

    """
    Test email address is normalized for new users.

    :param email:
    :param username:
    :param email_expected_format:
    :return: None
    """

    test_user = get_user_model().objects.create_user(
        email=email, username=username, password='sample123'
    )

    assert test_user.email == email_expected_format


def test_new_user_without_email_raises_error() -> None:

    """
    Test that creating a user without an email raises a ValueError.

    :return: None
    """

    with pytest.raises(ValueError):
        get_user_model().objects.create_user(
            email='', username='test_user123', password='test123'
        )


def test_new_user_without_username_raises_error() -> None:

    """
    Test that creating a user without a username raises a ValueError.

    :return: None
    """

    with pytest.raises(ValueError):
        get_user_model().objects.create_user(
            email='test@example.com', username='', password='test123'
        )


def test_create_superuser_return_successful() -> None:

    """
    Test creating a superuser.

    :return: None
    """

    email = 'test@example.com'
    username = 'test_user'
    password = 'test_pass123'
    user = get_user_model().objects.create_superuser(
        email=email,
        username=username,
        password=password
    )

    assert user.is_verified is True
    assert user.is_staff is True
    assert user.is_superuser is True


def test_new_superuser_with_wrong_extra_field_raises_error() -> None:

    """
    Test that creating a superuser with a false 'is_superuser' field
    raises a ValueError.

    :return: None
    """

    with pytest.raises(ValueError):
        get_user_model().objects.create_superuser(
            email='test@example.com', username='test_user123',
            password='test123', is_superuser=False
        )
