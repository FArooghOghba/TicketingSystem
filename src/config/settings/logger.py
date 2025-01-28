import logging
import os
from logging.config import dictConfig

from config.env import BASE_DIR, env


environment = env('ENVIRONMENT')

# Ensure the directory exists
log_file_path = env("DJANGO_LOG_FILE", default="/vol/web/logs/logfile.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)


class PhoneNumberFilter(logging.Filter):

    """
    A logging filter that masks part of a phone number in log records.

    Attributes:
        display_digits (int): The number of visible digits at
        the end of the phone number.
    """

    def __init__(self, name: str = "", display_digits: int = 4) -> None:

        """
        Initializes the PhoneNumberFilter with the specified name and display_digits.

        Args:
            name (str): The name of the filter.
            display_digits (int): The number of phone number digits to reveal.
        """

        super().__init__(name)
        self.display_digits = display_digits

    def filter(self, record: 'logging.LogRecord') -> bool:

        """
        Masks the phone number in the log record if present.

        Args:
            record (logging.LogRecord): The log record potentially containing a phone number.

        Returns:
            bool: True if the record should be logged, False otherwise.
        """

        if "phone" in record.__dict__:
            phone_length = len(record.phone)  # type: ignore
            to_hide = "*" * (phone_length - self.display_digits)
            to_display = record.phone[-self.display_digits:]  # type: ignore
            record.phone = to_hide + to_display

        return super().filter(record)


def logger_config() -> None:

    """
    Configures the logging settings, including formatters, handlers, and filters.

    Sets up two logging formats:
    - Standard console output with timestamps and logger details.
    - JSON file format for structured logging.

    Also applies a PhoneNumberFilter to the file handler to mask phone numbers.
    """

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "hide_phone": {
                    "()": PhoneNumberFilter,
                    "display_digits": 10 if environment == "development" else 4,
                },
            },
            "formatters": {
                "standard": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)-10s| %(name)s(line: %(lineno)d)| %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03d %(levelname)s %(name)s line: %(lineno)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "rich.logging.RichHandler",
                    "formatter": "standard",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "WARNING",
                    "formatter": "file",
                    "filename": log_file_path,
                    "maxBytes": 1024 * 1024 * 10,  # 10MB
                    "backupCount": 10,
                    "encoding": "utf8",
                    "filters": ["hide_phone"],
                },
            },
            "loggers": {
                "ticketing_system": {
                    "level": "DEBUG" if environment == "development" else "INFO",
                    "handlers": ["console", "file"],
                }
            },
        }
    )


logger_config()
