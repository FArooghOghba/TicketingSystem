#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from config.env import BASE_DIR, env


env.read_env(os.path.join(BASE_DIR, ".env"))


def main() -> None:
    """
    Runs the Django management command specified in the command line arguments.

    :raises: ImportError: If Django is not installed or not available on the
           PYTHONPATH environment variable.
    """

    os.environ.setdefault(
        key='DJANGO_SETTINGS_MODULE', value=env('DJANGO_SETTINGS_MODULE')
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
