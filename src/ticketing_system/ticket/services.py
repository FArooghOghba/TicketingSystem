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


def assign_ticket(*, ticket: 'Ticket', staff_profile: 'Profile') -> 'Ticket':

    """
    Assigns the given ticket to a staff user.

    Args:
        ticket (Ticket): The ticket to assign.
        staff_profile (Profile): The profile of the staff user to assign the ticket to.

    Returns:
        Ticket: The updated ticket.
    """

    ticket.assigned_to = staff_profile
    ticket.status = TicketStatus.IN_PROGRESS
    ticket.save()
    return ticket


