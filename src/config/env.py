import enum
from typing import Type, TypeVar

import environ
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = environ.Path(__file__) - 3

env = environ.Env()

_E = TypeVar("_E", bound=enum.Enum)


def env_to_enum(enum_cls: Type[_E], value: str) -> _E:

    """
    Converts an environment variable value to an enum value.

    :param enum_cls: (Type[_E]): The enum class to convert the value to.
    :param value: (str): The value to convert.

    :return _E: The enum value that corresponds to the given value.

    raises: ImproperlyConfigured: If the value could not be found in the enum class.
    """

    for x in enum_cls:
        if x.value == value:
            return x

    raise ImproperlyConfigured(
        f"Env value {repr(value)} could not be found in {repr(enum_cls)}"
    )
