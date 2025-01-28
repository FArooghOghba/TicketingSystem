from typing import Callable, Dict

import pytest
from django.contrib.auth import get_user_model

from ticketing_system.tests.factories.user_factories import BaseUserFactory


User = get_user_model()


@pytest.fixture
def first_test_user_payload() -> Dict[str, str]:

    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: a dict test user payload
    """

    return BaseUserFactory.create_payload()


@pytest.fixture
def first_test_user_login_payload() -> Dict[str, str]:

    """
    Fixture for login a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to log in a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: a dict test user payload
    """

    return BaseUserFactory.login_payload()


@pytest.fixture
def first_test_superuser() -> 'User':

    """
    Fixture for creating a test superuser instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test superuser instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: a test user instance
    """

    return BaseUserFactory.create_superuser()


@pytest.fixture
def first_test_user() -> 'User':

    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: a test user instance
    """

    return BaseUserFactory()


@pytest.fixture
def second_test_user() -> 'User':

    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: a test user instance
    """

    return BaseUserFactory()


@pytest.fixture
def third_test_user() -> 'User':

    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: a test user instance
    """

    return BaseUserFactory()


@pytest.fixture
def create_test_user() -> Callable[..., 'User']:

    """
    Fixture to create a test user using BaseUserFactory.

    Provides a callable function that accepts user attributes
    and creates a user instance using the factory.

    Returns:
        Callable[..., User]: A function that creates and returns a User instance.
    """

    def _create_test_user(**kwargs):
        kwargs.pop('confirm_password', None)  # Remove unnecessary fields
        return BaseUserFactory.create(**kwargs)

    return _create_test_user
