"""
WSGI config for ticketing_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from config.env import env


os.environ.setdefault(
    key='DJANGO_SETTINGS_MODULE', value=env('DJANGO_SETTINGS_MODULE')
)

application = get_wsgi_application()
