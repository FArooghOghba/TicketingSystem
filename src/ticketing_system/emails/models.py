from django.db import models

from ticketing_system.core.models import BaseModel


class Email(BaseModel):

    """
    Represents an email to be sent.

    Fields:
        - status (str): The current status of the email, using predefined choices.
        - from_email (str): The sender's email address.
        - to_email (str): The recipient's email address.
        - subject (str): The email subject.
        - message (str): The plain-text body of the email.
        - html (str): The HTML body of the email (optional).
        - sent_at (datetime): The timestamp when the email was successfully sent.
    """

    class Status(models.TextChoices):
        READY = ("READY", "Ready") # Email is ready to be sent.
        SENDING = ("SENDING", "Sending") # Email is in the process of being sent.
        SENT = ("SENT", "Sent") # Email has been successfully sent.
        FAILED = ("FAILED", "Failed") # Email failed to send.

    status = models.CharField(
        max_length=255, db_index=True, choices=Status.choices, default=Status.READY,
        help_text="The current status of the email.",
    )

    from_email = models.EmailField(
        help_text="The email address of the sender."
    )
    to_email = models.EmailField(
        help_text="The email address of the recipient."
    )
    subject = models.CharField(
        max_length=255,
        help_text="The subject of the email."
    )
    message = models.TextField(
        help_text="The plain-text body of the email."
    )

    html = models.TextField(
        help_text="The HTML content of the email (optional)."
    )
    sent_at = models.DateTimeField(
        blank=True, null=True,
        help_text="The timestamp when the email was sent (if applicable)."
    )

    def __str__(self) -> str:

        """
        Returns a string representation of the email, including
        its subject and status.
        """

        return f"{self.subject} ({self.get_status_display()})"
