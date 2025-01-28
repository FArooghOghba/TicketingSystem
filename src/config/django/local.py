from .base import *  # noqa


INSTALLED_APPS.append("debug_toolbar")
MIDDLEWARE.insert(
    0,
    "debug_toolbar.middleware.DebugToolbarMiddleware"
)

if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
