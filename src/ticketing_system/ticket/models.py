import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ticketing_system.core.models import BaseModel
from ticketing_system.users.models import UserRole


class TicketStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    IN_PROGRESS = "in_progress", _("In Progress")
    CLOSED = "closed", _("Closed")


class TicketPriority(models.TextChoices):
    LOW = "low", _("Low")
    MEDIUM = "medium", _("Medium")
    HIGH = "high", _("High")
    URGENT = "urgent", _("Urgent")


class Ticket(BaseModel):

    """
    Model representing a support ticket.
    """

    ticket_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index = True,
        verbose_name=_("Ticket ID"),
        help_text=_("Unique identifier for this ticket.")
    )

    created_by = models.ForeignKey(
        to='users.Profile',
        on_delete=models.CASCADE,
        db_index = True,
        related_name="tickets",
        verbose_name=_("Profile"),
        help_text=_("Profile who created the ticket.")
    )

    assigned_to = models.ForeignKey(
        to='users.Profile',
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
        limit_choices_to={'role': UserRole.STAFF},
        verbose_name=_("Assigned To"),
        help_text=_("The support agent handling the ticket.")
    )

    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
        help_text=_("Short summary of the issue.")
    )

    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Detailed description of the issue.")
    )

    file = models.FileField(
        upload_to="tickets/files/",
        blank=True,
        null=True,
        verbose_name=_("Attachment"),
        help_text=_("Optional file attachment.")
    )

    status = models.CharField(
        max_length=15,
        choices=TicketStatus.choices,
        default=TicketStatus.PENDING,
        db_index = True,
        verbose_name=_("Status"),
        help_text=_("Current status of the ticket.")
    )

    priority = models.CharField(
        max_length=10,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
        db_index=True,
        verbose_name=_("Priority"),
        help_text=_("Priority level of the ticket.")
    )

    class Meta:

        ordering = ["-updated_at", "-created_at"]
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self) -> str:
        return f"{self.subject} ({self.get_status_display()})"
