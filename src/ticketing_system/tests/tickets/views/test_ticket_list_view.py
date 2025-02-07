from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.urls import reverse

from ticketing_system.ticket.models import TicketStatus

if TYPE_CHECKING:
    from django.test import Client
    from ticketing_system.users.models import Profile
    from ticketing_system.ticket.models import Ticket


pytestmark = pytest.mark.django_db

User = get_user_model()

TICKET_LIST_URL = reverse('tickets:list')
USER_LOGIN_URL = reverse('auth:login')


def test_get_request_ticket_list_view_for_admin_users_return_successful(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that an admin user can retrieve all tickets.

    - Logs in as an admin.
    - Sends a GET request to the ticket list endpoint.
    - Asserts the response is successful (200 OK).
    - Ensures that all 5 test tickets are visible.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    response = client.get(path=TICKET_LIST_URL)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['tickets']) == 5


def test_get_request_ticket_list_view_for_staff_users_return_successful(
        client: 'Client', first_test_staff_user_profile: 'Profile',
        five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that a staff user can only see assigned tickets.

    - Assigns two tickets to the staff user.
    - Logs in as the staff user.
    - Sends a GET request to the ticket list endpoint.
    - Asserts that only the assigned tickets are visible.
    """

    first_ticket = five_test_tickets[0]
    first_ticket.assigned_to = first_test_staff_user_profile
    first_ticket.save()

    second_ticket = five_test_tickets[1]
    second_ticket.assigned_to = first_test_staff_user_profile
    second_ticket.save()

    staff_user = first_test_staff_user_profile.user
    client.force_login(staff_user)

    response = client.get(path=TICKET_LIST_URL)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['tickets']) == 2


def test_get_request_ticket_list_view_for_customer_return_successful(
        client: 'Client', first_test_user_profile: 'Profile',
        five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that a customer can only see tickets they created.

    - Assigns two tickets to the customer as the creator.
    - Logs in as the customer.
    - Sends a GET request to the ticket list endpoint.
    - Asserts that only the created tickets are visible.
    """

    first_ticket = five_test_tickets[0]
    first_ticket.created_by = first_test_user_profile
    first_ticket.save()

    second_ticket = five_test_tickets[1]
    second_ticket.created_by = first_test_user_profile
    second_ticket.save()

    customer_user = first_test_user_profile.user
    client.force_login(customer_user)

    response = client.get(path=TICKET_LIST_URL)
    assert len(response.context['tickets']) == 2


def test_get_request_ticket_list_view_for_unauthenticated_user_redirect(
        client: 'Client', five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that an unauthenticated user is redirected to the login page.

    - Sends a GET request to the ticket list endpoint without authentication.
    - Asserts that the response is a redirect (302 FOUND).
    - Ensures the redirection URL starts with the login URL.
    """

    response = client.get(path=TICKET_LIST_URL)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(USER_LOGIN_URL)


def test_get_request_ticket_list_view_context_admin_data_return_successful(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_staff_user_profile: 'Profile',
        five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that the context for an admin user is correctly populated with
    aggregated ticket counts.

    Steps:
      - Assign two tickets to a staff user (one IN_PROGRESS, one CLOSED) for
      demonstration.
      - Log in as an admin user.
      - Send a GET request to the ticket list view.
      - Assert that the 'user_profile' is in the context and that the aggregated
      counts are correct.
    """

    # Modify the first two tickets to simulate assignment and status updates.
    first_ticket = five_test_tickets[0]
    first_ticket.assigned_to = first_test_staff_user_profile
    first_ticket.status = TicketStatus.IN_PROGRESS
    first_ticket.save()

    second_ticket = five_test_tickets[1]
    second_ticket.assigned_to = first_test_staff_user_profile
    second_ticket.status = TicketStatus.CLOSED
    second_ticket.save()

    # For admin, assume that there are 3 pending tickets in total (from other fixtures)
    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    response = client.get(path=TICKET_LIST_URL)
    assert 'user_profile' in response.context

    user_profile = response.context['user_profile']
    assert user_profile == first_test_admin_user_profile

    # Check aggregated counts (adjust the expected values as per your test setup)
    assert user_profile.pending_tickets_count == 3
    assert user_profile.in_progress_tickets_count == 1
    assert user_profile.closed_tickets_count == 1


def test_get_request_ticket_list_view_context_staff_data_return_successful(
        client: 'Client', first_test_staff_user_profile: 'Profile',
        five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that a staff user's profile context is correctly populated with
    assigned ticket counts.

    Steps:
      - Assign two tickets to the staff user (one IN_PROGRESS, one CLOSED).
      - Log in as the staff user.
      - Send a GET request to the ticket list view.
      - Assert that the 'user_profile' is in the context and that the assigned
      ticket counts are correct.
    """

    first_ticket = five_test_tickets[0]
    first_ticket.assigned_to = first_test_staff_user_profile
    first_ticket.status = TicketStatus.IN_PROGRESS
    first_ticket.save()

    second_ticket = five_test_tickets[1]
    second_ticket.assigned_to = first_test_staff_user_profile
    second_ticket.status = TicketStatus.CLOSED
    second_ticket.save()

    staff_user = first_test_staff_user_profile.user
    client.force_login(staff_user)

    response = client.get(path=TICKET_LIST_URL)
    assert 'user_profile' in response.context

    user_profile = response.context['user_profile']
    assert user_profile == first_test_staff_user_profile
    assert user_profile.in_progress_tickets_count == 1
    assert user_profile.closed_tickets_count == 1


def test_get_request_ticket_list_view_context_customer_data_return_successful(
        client: 'Client', first_test_staff_user_profile: 'Profile',
        first_test_user_profile: 'Profile',
        five_test_tickets: QuerySet['Ticket']
) -> None:

    """
    Test that a customer user's profile context is correctly populated
    with ticket creation counts.

    Steps:
      - Create three tickets by the customer, with varying statuses.
      - Two tickets are created by the customer: one IN_PROGRESS and two CLOSED.
      - Log in as the customer.
      - Send a GET request to the ticket list view.
      - Assert that the 'user_profile' is in the context and that the created
      ticket counts are correct.
    """

    first_ticket = five_test_tickets[0]
    first_ticket.created_by = first_test_user_profile
    first_ticket.assigned_to = first_test_staff_user_profile
    first_ticket.status = TicketStatus.IN_PROGRESS
    first_ticket.save()

    second_ticket = five_test_tickets[1]
    second_ticket.created_by = first_test_user_profile
    second_ticket.assigned_to = first_test_staff_user_profile
    second_ticket.status = TicketStatus.CLOSED
    second_ticket.save()

    third_ticket = five_test_tickets[2]
    third_ticket.created_by = first_test_user_profile
    third_ticket.assigned_to = first_test_staff_user_profile
    third_ticket.status = TicketStatus.CLOSED
    third_ticket.save()

    customer_user = first_test_user_profile.user
    client.force_login(customer_user)

    response = client.get(path=TICKET_LIST_URL)
    assert 'user_profile' in response.context

    user_profile = response.context['user_profile']
    assert user_profile == first_test_user_profile
    assert user_profile.pending_tickets_count == 0
    assert user_profile.in_progress_tickets_count == 1
    assert user_profile.closed_tickets_count == 2
