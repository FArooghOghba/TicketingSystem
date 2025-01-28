"""
ASGI config for ticketing_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from config.env import env


os.environ.setdefault(
    key='DJANGO_SETTINGS_MODULE', value=env('DJANGO_SETTINGS_MODULE')
)


application = get_asgi_application()
