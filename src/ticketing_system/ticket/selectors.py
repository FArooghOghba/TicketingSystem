from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ticketing_system.users.models import Profile, UserRole
from ticketing_system.ticket.models import Ticket


def get_user_tickets(*, user_profile: 'Profile') -> QuerySet['Ticket']:

    """
    Retrieve tickets based on the user's role.

    - If the user is an ADMIN, return all tickets.
    - If the user is a STAFF member, return only tickets assigned to them.
    - If the user is a CUSTOMER, return only tickets they created.

    Args:
        user_profile (Profile): The profile of the logged-in user.

    Returns:
        QuerySet[Ticket]: A queryset containing tickets relevant to the user.
    """

    role = user_profile.role

    if role == UserRole.ADMIN:
        return Ticket.objects.select_related("created_by", "created_by__user").all()

    if role == UserRole.STAFF:
        return (
            Ticket.objects
            .select_related("created_by", "created_by__user")
            .filter(assigned_to=user_profile)
        )

    # Default for customers
    return Ticket.objects.select_related("created_by", "created_by__user").filter(
        created_by=user_profile
    )


def get_ticket_detail(*, user_profile: 'Profile', ticket_id: str) -> 'Ticket':

    """
    Fetches a ticket while enforcing role-based access.

    - Admins can view any ticket.
    - Staff users can only view tickets assigned to them.
    - Customers can only view tickets they created.

    Args:
        user_profile (Profile): The profile of the logged-in user.
        ticket_id (str): The unique ticket identifier.

    Returns:
        Ticket: The requested ticket if permitted.

    Raises:
        PermissionError: If the user does not have permission to view the ticket.
    """

    ticket = get_object_or_404(
        Ticket.objects
        .select_related("created_by", "created_by__user"), ticket_id=ticket_id
    )
    user_role = user_profile.role

    if user_role == UserRole.ADMIN:
        return ticket  # Admins can see all tickets

    if user_role == UserRole.STAFF and ticket.assigned_to == user_profile:
        return ticket  # Staff can only see assigned tickets

    if user_role == UserRole.CUSTOMER and ticket.created_by == user_profile:
        return ticket  # Customers can only see their own tickets

    raise PermissionError("You do not have permission to view this ticket.")
