from django.db.models import QuerySet
from ticketing_system.users.models import Profile, UserRole
from ticketing_system.ticket.models import Ticket

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
        return Ticket.objects.all()

    if role == UserRole.STAFF:
        return Ticket.objects.filter(assigned_to=user_profile)

    # Default for customers
    return Ticket.objects.filter(
        created_by=user_profile
    )
