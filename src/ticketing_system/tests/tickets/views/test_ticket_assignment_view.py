from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse


if TYPE_CHECKING:
    from django.test import Client
    from ticketing_system.users.models import Profile
    from ticketing_system.ticket.models import Ticket


pytestmark = pytest.mark.django_db


TICKET_ASSIGNMENT_URL = lambda ticket_id: reverse(
    viewname="tickets:assign", kwargs={"ticket_id": ticket_id}
)
TICKET_ASSIGNMENT_REDIRECT_URL = lambda ticket_id: reverse(
    viewname="tickets:detail", kwargs={"ticket_id": ticket_id}
)


def test_post_request_ticket_assignment_view_assigned_to_staff_return_successful(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_staff_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket',
) -> None:

    """
    Test that an admin user can successfully assign a ticket to a staff user.

    Steps:
      - Log in as an admin user.
      - Create a ticket with status 'pending'.
      - POST valid assignment data (staff profile's pk) to the assignment endpoint.
      - Assert that the view returns a redirect.
      - Verify that the ticket's assigned_to field is updated to the staff profile.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    form_data = {
        "assigned_to": first_test_staff_user_profile.pk
    }
    ticket_assignment_url = TICKET_ASSIGNMENT_URL(first_test_pending_ticket.ticket_id)
    response = client.post(path=ticket_assignment_url, data=form_data)

    # Check that the response redirects to the ticket detail page
    assert response.status_code == HTTPStatus.FOUND

    # Verify that redirection is to the ticket list page.
    ticket_assignment_redirect_url = TICKET_ASSIGNMENT_REDIRECT_URL(
        first_test_pending_ticket.ticket_id
    )
    assert response.url == ticket_assignment_redirect_url

    success_message = "Ticket assigned successfully."
    assert success_message in str([m.message for m in get_messages(response.wsgi_request)])

    # Re-fetch the ticket from the database to verify assignment.
    first_test_pending_ticket.refresh_from_db()
    assert first_test_pending_ticket.assigned_to == first_test_staff_user_profile


def test_post_request_ticket_assignment_view_with_non_admin_user_return_error(
        client: 'Client', first_test_user_profile: 'Profile',
        first_test_staff_user_profile: 'Profile', first_test_pending_ticket: 'Ticket'
) -> None:

    """
    Test that a non-admin user cannot assign a ticket.

    Steps:
      - Log in as a customer.
      - Create a pending ticket.
      - Attempt to assign the ticket to a staff user by POSTing assignment data.
      - Assert that the view returns a redirect (with an error message)
      and that the ticket is not assigned.
    """

    customer_user = first_test_user_profile.user
    client.force_login(customer_user)

    ticket_assignment_url = TICKET_ASSIGNMENT_URL(first_test_pending_ticket.ticket_id)
    form_data = {"assigned_to": first_test_staff_user_profile.pk}

    response = client.post(path=ticket_assignment_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND

    error_message = "You don't have permission to assign tickets."
    assert error_message in str([m.message for m in get_messages(response.wsgi_request)])

    # Verify that the ticket is not assigned.
    first_test_pending_ticket.refresh_from_db()
    assert first_test_pending_ticket.assigned_to is None


def test_post_request_ticket_assignment_view_with_invalid_form_data_return_error(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket'
) -> None:

    """
    Test that an invalid assignment form submission results in an error
    and no ticket assignment.

    Steps:
      - Log in as an admin user.
      - Create a pending ticket.
      - POST invalid form data (e.g. missing required 'assigned_to' field).
      - Assert that the view returns a redirect and the ticket remains unassigned.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    ticket_assignment_url = TICKET_ASSIGNMENT_URL(first_test_pending_ticket.ticket_id)

    # Provide an empty form data to simulate an invalid submission.
    form_data = {}
    response = client.post(path=ticket_assignment_url, data=form_data)

    # Expect a redirect after invalid submission.
    assert response.status_code == HTTPStatus.FOUND

    error_message = 'Invalid assignment form submission.'
    assert error_message in str([m.message for m in get_messages(response.wsgi_request)])

    first_test_pending_ticket.refresh_from_db()
    assert first_test_pending_ticket.assigned_to is None


def test_post_request_ticket_assignment_view_assigned_to_none_staff_return_error(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_user_profile: 'Profile', first_test_pending_ticket: 'Ticket',
) -> None:

    """
    Test that a ticket cannot assign to a non staff user.

    Steps:
      - Log in as a admin.
      - Create a pending ticket.
      - Attempt to assign the ticket to a non staff user by POSTing assignment data.
      - Assert that the view returns a redirect (with an error message)
      and that the ticket is not assigned.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    form_data = {
        "assigned_to": first_test_user_profile.pk
    }
    ticket_assignment_url = TICKET_ASSIGNMENT_URL(first_test_pending_ticket.ticket_id)
    response = client.post(path=ticket_assignment_url, data=form_data)

    # Expect a redirect after invalid submission.
    assert response.status_code == HTTPStatus.FOUND

    error_message = "'Invalid assignment form submission."
    assert error_message in str([m.message for m in get_messages(response.wsgi_request)])

    first_test_pending_ticket.refresh_from_db()
    assert first_test_pending_ticket.assigned_to is None