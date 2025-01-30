from typing import Dict

from django.contrib.auth import get_user_model
from factory import PostGenerationMethodCall, Sequence
from factory.django import DjangoModelFactory


User = get_user_model()


class BaseUserFactory(DjangoModelFactory):

    """
    Factory class for creating instances of the BaseUser model.

    This factory provides a convenient way to generate
    test data for the BaseUser model in Django.
    It automatically generates unique email addresses,
    usernames, and sets a default password for each
    created instance.
    """

    class Meta:
        model = User

    email = Sequence(
        lambda instance_num: f'test_user_{instance_num}@example.com'
    )

    username = Sequence(
        lambda instance_num: f'test_user_{instance_num}'
    )

    password = PostGenerationMethodCall(
        'set_password', 'Test_passw0rd'
    )

    is_verified = True  # Default to a verified user for convenience
    is_active = True  # Default to activate user for convenience

    @classmethod
    def create_payload(cls) -> Dict[str, str]:

        """
        A class method that generates a payload dictionary for creating
        a user via the API.
        :return: generate a payload dictionary with consistent values
        for creating users via the API.
        """

        test_user = cls.build()
        return {
            'email': str(test_user.email),
            'username': str(test_user.username),
            'password1': 'Test_passw0rd',
            'password2': 'Test_passw0rd',
        }

    @classmethod
    def login_payload(cls) -> Dict[str, str]:

        """
        A class method that generates a payload dictionary for login
        a user via the API.
        :return: generate a payload dictionary with consistent values
        for logging users via the API.
        """

        test_user = cls.create()
        return {
            'email': str(test_user.email),
            'password': 'Test_passw0rd',
        }

    @classmethod
    def unverified_login_payload(cls) -> Dict[str, str]:

        """
        A class method that generates a payload dictionary for login
        an unverified user via the API.
        :return: generate a payload dictionary with consistent values
        for logging users.
        """

        test_user = cls.create(is_verified=False)
        return {
            'email': str(test_user.email),
            'password': 'Test_passw0rd',
        }

    @classmethod
    def nonactive_login_payload(cls) -> Dict[str, str]:

        """
        A class method that generates a payload dictionary for login
        a nonactive user via the API.
        :return: generate a payload dictionary with consistent values
        for logging users.
        """

        test_user = cls.create(is_active=False)
        return {
            'email': str(test_user.email),
            'password': 'Test_passw0rd',
        }

    @classmethod
    def create_superuser(cls) -> 'User':

        """
        A class method that creates a superuser instance.

        :return: The newly created superuser instance.
        """

        test_user = cls.build()

        superuser = User.objects.create_superuser(
            email=str(test_user.email),
            username=str(test_user.username),
            password='Test_passw0rd',
        )

        return superuser
