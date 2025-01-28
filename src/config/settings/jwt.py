from datetime import timedelta


# For more settings
# Read everything from here
# https://styria-digital.github.io/django-rest-framework-jwt/#additional-settings

# Default to 7 days
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}