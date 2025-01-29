from datetime import timedelta

from config.env import env


# Default email configurations
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")

DEFAULT_REGISTRATION_EMAIL_SUBJECT = "Welcome to Our Service!"
DEFAULT_REGISTRATION_EMAIL_TEMPLATE_TXT = "emails/registration_email.txt"
DEFAULT_REGISTRATION_EMAIL_TEMPLATE_HTML = "emails/registration_email.html"
DEFAULT_REGISTRATION_EMAIL_JWT_MAX_AGE = timedelta(minutes=30)


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
