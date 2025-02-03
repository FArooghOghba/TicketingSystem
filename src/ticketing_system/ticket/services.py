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


def close_ticket(
        *, user_profile: 'Profile', ticket: 'Ticket', closing_message: str = ""
) -> 'Ticket':

    """
    Closes a ticket and updates its status to CLOSED.

    This function checks if the user has permission to close the ticket (only admin or staff users)
    and that the ticket is not already closed. It then updates the ticket's status to CLOSED.

    Args:
        user_profile (Profile): The profile of the user attempting to close the ticket.
        ticket (Ticket): The ticket to be closed.
        closing_message (str, optional): An optional closing message detailing the resolution.
            (Currently not recorded; can be used to create a TicketReply in the future.)

    Raises:
        PermissionDenied: If the user does not have permission (i.e., is not admin or staff).
        ValueError: If the ticket is already closed.

    Returns:
        Ticket: The updated ticket with status set to CLOSED.
    """

    if user_profile.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise PermissionDenied("You do not have permission to close this ticket.")

    if ticket.status == TicketStatus.CLOSED:
        raise ValueError("Ticket is already closed.")

    # Optionally, record the closing message as a TicketReply
    # if closing_message:
    #     TicketReply.objects.create(
    #         ticket=ticket,
    #         sender=user_profile,
    #         message=closing_message,
    #     )

    # Update ticket status
    ticket.status = TicketStatus.CLOSED
    ticket.save()

    return ticket
