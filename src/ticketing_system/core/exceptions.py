from typing import Dict, Optional

from rest_framework.exceptions import APIException
from rest_framework import status


class ApplicationError(Exception):

    """
    An error that occurs during the execution of an application.
    """

    def __init__(
            self, message: str, extra: Optional[Dict[str, str]] = None
    ) -> None:

        """
        Initializes a new instance of the ApplicationError class.

        :param message (str): A string that describes the error.
            extra (dict, optional): A dictionary that contains additional
                information about the error, Defaults to None.
        :return: None
        """

        super().__init__(message)

        self.message = message
        self.extra = extra or {}


class UserNotActiveError(APIException):

    """
    Raised when an operation is attempted on an inactive user.
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "The user is inactive."
    default_code = "user_inactive"


class UserNotVerifiedError(APIException):

    """
    Raised when an operation is attempted on a user who hasn't been verified.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The user has not been verified."
    default_code = "user_not_verified"
