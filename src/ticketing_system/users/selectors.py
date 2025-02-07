from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from ticketing_system.users.models import Profile, UserRole
from ticketing_system.ticket.models import Ticket, TicketStatus
from ticketing_system.ticket.selectors import get_tickets_count


User = get_user_model()


def get_admin_user_profile(*, user: 'User') -> 'Profile':

    """
    Retrieves the admin user's profile and attaches aggregated
    ticket counts for all tickets.

    Args:
        user (User): The admin user.

    Returns:
        Profile: The admin Profile instance with attributes:
            - pending_tickets_count
            - in_progress_tickets_count
            - closed_tickets_count
    """

    admin_user_profile = Profile.objects.select_related('user').get(user=user)

    # Attach aggregated counts to the profile instance as attributes
    aggregated_counts = get_tickets_count()
    admin_user_profile.pending_tickets_count = aggregated_counts.get('pending_tickets_count', 0)
    admin_user_profile.in_progress_tickets_count = aggregated_counts.get('in_progress_tickets_count', 0)
    admin_user_profile.closed_tickets_count = aggregated_counts.get('closed_tickets_count', 0)

    return admin_user_profile


def get_staff_user_profile(*, user: 'User') -> 'Profile':

    """
    Retrieves the staff user's profile and annotates it with ticket
    counts for assigned tickets.

    Args:
        user (User): The staff user.

    Returns:
        Profile: The staff Profile instance with attributes:
            - in_progress_tickets_count: Count of assigned tickets in progress.
            - closed_tickets_count: Count of assigned tickets that are closed.
    """

    staff_user_profile = Profile.objects.select_related('user').filter(user=user).annotate(
        in_progress_tickets_count=Count(
            'assigned_tickets',
            filter=Q(assigned_tickets__status=TicketStatus.IN_PROGRESS)
        ),
        closed_tickets_count=Count(
            'assigned_tickets',
            filter=Q(assigned_tickets__status=TicketStatus.CLOSED)
        ),
    ).first()

    return staff_user_profile


def get_customer_user_profile(*, user: 'User') -> 'Profile':

    """
    Retrieves the customer user's profile and annotates it with
    ticket counts for created tickets.

    Args:
        user (User): The customer user.

    Returns:
        Profile: The customer Profile instance with attributes:
            - pending_tickets_count: Count of created tickets pending.
            - in_progress_tickets_count: Count of created tickets in progress.
            - closed_tickets_count: Count of created tickets that are closed.
    """

    customer_user_profile = Profile.objects.select_related('user').filter(user=user).annotate(
        pending_tickets_count=Count(
            'tickets',
            filter=Q(tickets__status=TicketStatus.PENDING)
        ),
        in_progress_tickets_count=Count(
            'tickets',
            filter=Q(tickets__status=TicketStatus.IN_PROGRESS)
        ),
        closed_tickets_count=Count(
            'tickets',
            filter=Q(tickets__status=TicketStatus.CLOSED)
        ),
    ).first()

    return customer_user_profile


def get_user_profile(*, user: 'User') -> 'Profile':

    """
    Retrieves the profile for the given user, applying role-specific aggregation.

    Args:
        user (User): The user whose profile is to be retrieved.

    Returns:
        Profile: The user's Profile instance annotated with ticket counts based on role.
    """

    user = User.objects.select_related('profile').get(pk=user.pk)
    user_role = user.profile.role

    if user_role == UserRole.ADMIN:
        return get_admin_user_profile(user=user)

    if user_role == UserRole.STAFF:
        return get_staff_user_profile(user=user)

    return get_customer_user_profile(user=user)