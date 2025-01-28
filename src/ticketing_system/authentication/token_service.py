from datetime import timedelta
from typing import Dict, Optional, TypeVar, Union

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from config.env import env


# Application domain, configurable via environment variable
APP_DOMAIN = env("APP_DOMAIN", default="http://localhost:8000")

# Define a generic User type for type annotations
User = TypeVar("User", bound=get_user_model())


class TokenService:

    """
    Service class for handling token-related functionalities.

    Provides methods to generate JWT tokens and construct URLs
    containing tokens for specific user actions.
    """

    @staticmethod
    def generate_jwt_token(
            user: 'User', token_type: Optional[str] = None,
            expiry: timedelta = None
    ) -> Union[str, Dict[str, str]]:

        """
        Generate JWT tokens for a user.

        Args:
            user (User): The user for whom the tokens are generated.
            token_type (Optional[str]): Type of the token ('access', 'refresh', or None).
                If `None`, both `access` and `refresh` tokens are returned.
            expiry (timedelta, optional): Token expiration duration. Applies only if
                generating a single token. Defaults to standard lifetimes if not provided.

        Returns:
            Union[str, Dict[str, str]]: If `token_type` is provided, returns the corresponding
            token as a string. If `token_type` is `None`, returns a dictionary with both tokens.
        """

        refresh = RefreshToken.for_user(user)

        # Set custom expiry if provided
        if expiry:
            refresh.set_exp(lifetime=expiry)

        if token_type == 'access':
            return str(refresh.access_token)
        elif token_type == 'refresh':
            return str(refresh)

        # Return both tokens if no specific type is requested
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }

    @staticmethod
    def generate_url_with_token(
            user: 'User', token_type: str, expiry: timedelta, view_name: str
    ) -> str:

        """
        Generate a URL containing an embedded JWT token.

        Args:
            user (User): The user for whom the token is generated.
            token_type (str): Type of the token ('access' or 'refresh').
            expiry (timedelta): Token expiration duration.
            view_name (str): The name of the view that the URL points to.

        Returns:
            str: A complete URL with the JWT token embedded as an argument.
        """

        # Generate the token
        token = TokenService.generate_jwt_token(user, token_type, expiry)

        # Construct the URL by reversing the view name and appending the token
        url = reverse(view_name, args=[token])
        return f'{APP_DOMAIN}{url}'
