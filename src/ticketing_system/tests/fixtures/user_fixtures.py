from typing import Callable, Dict, TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model

from ticketing_system.users.models import UserRole
from ticketing_system.tests.factories.user_factories import BaseUserFactory
from ticketing_system.tests.factories.profile_factories import UserProfileFactory

if TYPE_CHECKING:
    from ticketing_system.users.models import Profile


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
def first_test_unverified_user_login_payload() -> Dict[str, str]:

    """
    Fixture for login an unverified test user instance.

    This fixture uses the `BaseUserFactory` factory
    to log in an unverified test user instance. The created user
    can be used in tests to simulate an unverified user with predefined
    attributes for testing various scenarios.

    :return: a dict test user payload
    """

    return BaseUserFactory.unverified_login_payload()


@pytest.fixture
def first_test_nonactive_user_login_payload() -> Dict[str, str]:

    """
    Fixture for login a nonactive test user instance.

    This fixture uses the `BaseUserFactory` factory
    to log in a nonactive test user instance. The created user
    can be used in tests to simulate a nonactive user with predefined
    attributes for testing various scenarios.

    :return: a dict test user payload
    """

    return BaseUserFactory.nonactive_login_payload()


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
def first_test_unverified_user() -> 'User':

    """
    Fixture for creating an unverified test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.

    :return: an unverified user instance
    """

    return BaseUserFactory(is_verified=False)


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


@pytest.fixture
def first_test_user_profile() -> 'Profile':

    """
    Fixture to create a test profile for a regular user.

    Returns:
    - A Profile instance with default role as CUSTOMER.
    """

    return UserProfileFactory()


@pytest.fixture
def second_test_user_profile() -> 'Profile':

    """
    Fixture to create a test profile for a regular user.

    Returns:
    - A Profile instance with default role as CUSTOMER.
    """

    return UserProfileFactory()


@pytest.fixture
def first_test_staff_user_profile() -> 'Profile':

    """
    Fixture to create a test profile for a staff user.

    Customization:
    - Sets the role of the user to STAFF for testing staff-specific functionalities.

    Returns:
    - A Profile instance with role set to STAFF.
    """

    return UserProfileFactory(role=UserRole.STAFF)
