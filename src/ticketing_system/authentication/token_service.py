import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from jwt import ExpiredSignatureError, decode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, Token

from config.env import env
from ticketing_system.core.exceptions import ApplicationError


logger = logging.getLogger(__name__)


# Application domain, configurable via environment variable
APP_DOMAIN = env("APP_DOMAIN", default="http://localhost:8000")

User = get_user_model()


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

    @staticmethod
    def validate_token(
            token: 'Token', max_age: timedelta = None
    ) -> 'User':

        """
        Validate a JWT token and return the associated user.

        Args:
            token (str): The JWT token to validate.
            max_age (timedelta, optional): Maximum allowed token age. If provided,
                the method ensures the token has not exceeded this age.

        Returns:
            User: The authenticated user instance.

        Raises:
            ApplicationError: Raised if the token is invalid, expired, or malformed.
            User.DoesNotExist: Raised if the user associated with the token does not exist.
        """

        try:
            # Decode and verify token
            decoded_token = decode(
                jwt=token, key=env('SECRET_KEY'), algorithms=['HS256']
            )

            # Verify expiration (automatically checked by SimpleJWT)
            current_time = datetime.now().timestamp()
            if (current_time - decoded_token['iat']) > max_age.total_seconds():
                raise ExpiredSignatureError()

            # Get user
            user_id = decoded_token['user_id']
            user = User.objects.get(pk=user_id)

            return user

        except (ExpiredSignatureError, TokenError, InvalidToken) as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise ApplicationError("Invalid or expired token")
        except ObjectDoesNotExist:
            logger.error("User not found for valid token")
            raise User.DoesNotExist
