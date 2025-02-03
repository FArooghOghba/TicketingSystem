from typing import TYPE_CHECKING
from http import HTTPStatus

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django.test import Client
    from ticketing_system.users.models import Profile
    from ticketing_system.ticket.models import Ticket


pytestmark = pytest.mark.django_db


TICKET_DETAIL_URL = lambda ticket_id: reverse(
    viewname="tickets:detail", kwargs={"ticket_id": ticket_id}
)


def test_get_request_ticket_detail_view_admin_user_return_successful(
        client: 'Client', first_test_admin_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket'
) -> None:

    """
    Test that an admin user can access the detail view for any ticket.

    Steps:
      - Log in as an admin.
      - Create a ticket using the factory.
      - Issue a GET request to the detail view URL.
      - Assert that the response is 200 OK and the correct ticket is in context.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    url = TICKET_DETAIL_URL(first_test_pending_ticket.ticket_id)
    response = client.get(path=url)
    assert response.status_code == 200

    assert "ticket" in response.context
    assert response.context["ticket"].ticket_id == first_test_pending_ticket.ticket_id
    assert "user_profile" in response.context


def test_get_request_ticket_detail_view_staff_user_assigned_return_successful(
        client: 'Client', first_test_staff_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket'
):

    """
    Test that a staff user can access a ticket detail view if the ticket is assigned to them.

    Steps:
      - Log in as a staff user.
      - Create a ticket and assign it to this staff profile.
      - Issue a GET request to the detail view.
      - Assert that the ticket is accessible (response status 200).
    """

    staff_user = first_test_staff_user_profile.user
    client.force_login(staff_user)

    # Assign the ticket to this staff user
    first_test_pending_ticket.assigned_to = first_test_staff_user_profile
    first_test_pending_ticket.save()

    url = TICKET_DETAIL_URL(first_test_pending_ticket.ticket_id)
    response = client.get(path=url)
    assert response.status_code == HTTPStatus.OK
    assert response.context["ticket"].ticket_id == first_test_pending_ticket.ticket_id


def test_get_request_ticket_detail_view_staff_user_not_assigned_return_error(
        client: 'Client', first_test_staff_user_profile: 'Profile',
        first_test_user_profile: 'Profile', first_test_pending_ticket: 'Ticket'
) -> None:

    """
    Test that a staff user cannot access a ticket that is not assigned to them.

    Steps:
      - Log in as a staff user.
      - Create a ticket that is not assigned to the staff user.
      - Issue a GET request to the ticket detail view.
      - Assert that the view raises Http404.
    """

    staff_user = first_test_staff_user_profile.user
    client.force_login(staff_user)

    # Ensure the ticket is created by another profile (customer)
    first_test_pending_ticket.created_by = first_test_user_profile
    first_test_pending_ticket.assigned_to = None  # Not assigned to the staff user
    first_test_pending_ticket.save()

    url = TICKET_DETAIL_URL(first_test_pending_ticket.ticket_id)
    response = client.get(path=url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_request_ticket_detail_view_customer_user_return_successful(
        client: 'Client', first_test_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket'
) -> None:

    """
    Test that a customer can view the detail page for a ticket they created.

    Steps:
      - Log in as a customer.
      - Create a ticket with the customer as the creator.
      - Issue a GET request to the detail view.
      - Assert that the response is 200 OK.
    """

    customer_user = first_test_user_profile.user
    client.force_login(customer_user)

    first_test_pending_ticket.created_by = first_test_user_profile
    first_test_pending_ticket.save()

    url = TICKET_DETAIL_URL(first_test_pending_ticket.ticket_id)
    response = client.get(path=url)

    assert response.status_code == HTTPStatus.OK
    assert response.context["ticket"].ticket_id == first_test_pending_ticket.ticket_id


def test_get_request_ticket_detail_view_customer_not_owner_return_error(
        client: 'Client', first_test_user_profile: 'Profile',
        first_test_staff_user_profile: 'Profile',
        first_test_pending_ticket: 'Ticket',
) -> None:

    """
    Test that a customer cannot view a ticket they did not create.

    Steps:
      - Log in as a customer.
      - Create a ticket that was created by a staff member.
      - Issue a GET request to the ticket detail view.
      - Assert that the view raises Http404.
    """

    customer_user = first_test_user_profile.user
    client.force_login(customer_user)

    first_test_pending_ticket.created_by = first_test_staff_user_profile
    first_test_pending_ticket.save()

    url = TICKET_DETAIL_URL(first_test_pending_ticket.ticket_id)
    response = client.get(path=url)
    assert response.status_code == HTTPStatus.NOT_FOUND
