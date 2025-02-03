from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from django.contrib.messages import get_messages

from ticketing_system.ticket.models import Ticket, TicketStatus

if TYPE_CHECKING:
    from django.test import Client
    from ticketing_system.users.models import Profile
    from ticketing_system.ticket.models import Ticket


pytestmark = pytest.mark.django_db

TICKET_CLOSE_URL = lambda ticket_id: reverse(
    viewname="tickets:close", kwargs={"ticket_id": ticket_id}
)


def test_post_request_close_ticket_view_with_valid_data_return_successful(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_in_progress_ticket: 'Ticket'
) -> None:

    """
    Test that an admin user can successfully close a ticket.

    Steps:
      - Log in as an admin.
      - Create a ticket (with status PENDING or IN_PROGRESS).
      - POST valid form data (with an optional closing_message) to close the ticket.
      - Assert that the response is a redirect.
      - Verify that the ticket's status is updated to CLOSED.
      - Check that a success message is present.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    ticket_assignment_url = TICKET_CLOSE_URL(first_test_in_progress_ticket.ticket_id)
    form_data = {"closing_message": "Issue resolved."}

    response = client.post(path=ticket_assignment_url, data=form_data)
    # Expect a redirect after successful closure.
    assert response.status_code == HTTPStatus.FOUND

    first_test_in_progress_ticket.refresh_from_db()
    assert first_test_in_progress_ticket.status == TicketStatus.CLOSED

    success_message = "Ticket successfully closed."
    assert success_message in str([m.message for m in get_messages(response.wsgi_request)])


def test_post_request_close_ticket_view_that_already_closed_return_error(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_closed_ticket: 'Ticket'
) -> None:

    """
    Test that attempting to close a ticket that is already closed returns an error.

    Steps:
      - Log in as an admin.
      - Create a ticket that is already CLOSED.
      - Submit the close ticket form.
      - Assert that the ticket remains CLOSED.
      - Verify that an error message is present indicating the ticket is already closed.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    ticket_assignment_url = TICKET_CLOSE_URL(first_test_closed_ticket.ticket_id)
    form_data = {"closing_message": "Attempting to close again."}

    response = client.post(path=ticket_assignment_url, data=form_data)
    # Expect a redirect (even on error) since our view always redirects.
    assert response.status_code == HTTPStatus.FOUND

    first_test_closed_ticket.refresh_from_db()
    assert first_test_closed_ticket.status == TicketStatus.CLOSED

    error_message = "Ticket is already closed."
    assert error_message in str([m.message for m in get_messages(response.wsgi_request)])


def test_post_request_close_ticket_view_by_non_admin_user_return_error(
        client: 'Client', first_test_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket'
) -> None:

    """
    Test that a non-admin (customer) user cannot close a ticket.

    Steps:
      - Log in as a customer.
      - Create a ticket.
      - Attempt to close the ticket via a POST request.
      - Assert that the view redirects and an error message is shown.
      - Verify that the ticket's status remains unchanged.
    """

    customer_user = first_test_user_profile.user
    client.force_login(customer_user)

    ticket_assignment_url = TICKET_CLOSE_URL(first_test_pending_ticket.ticket_id)
    form_data = {"closing_message": "Trying to close ticket."}

    response = client.post(path=ticket_assignment_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND

    # The ticket should remain unclosed.
    first_test_pending_ticket.refresh_from_db()
    assert first_test_pending_ticket.status != TicketStatus.CLOSED

    error_message = "You do not have permission to close this ticket."
    assert error_message in str([m.message for m in get_messages(response.wsgi_request)])
