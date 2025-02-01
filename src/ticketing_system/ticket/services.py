from django.core.exceptions import PermissionDenied
from ticketing_system.users.models import Profile, UserRole
from ticketing_system.ticket.models import Ticket
from ticketing_system.ticket.models import TicketStatus


def create_ticket(
        *, created_by: Profile, subject: str, description: str, file=None
) -> 'Ticket':

    """Creates a new ticket and updates the user’s pending ticket count."""

    ticket = Ticket.objects.create(
        created_by=created_by,
        subject=subject,
        description=description,
        file=file
    )
    return ticket


