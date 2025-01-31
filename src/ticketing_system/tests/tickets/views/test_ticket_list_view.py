from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


pytestmark = pytest.mark.django_db

User = get_user_model()

TICKET_LIST_URL = reverse('tickets:list')
USER_LOGIN_URL = reverse('auth:login')


def test_get_request_ticket_list_view_for_admin_users_return_successful(
        client, first_test_admin_user_profile, five_test_tickets
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
        client, first_test_staff_user_profile, five_test_tickets
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
        client, first_test_user_profile, five_test_tickets
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
        client, five_test_tickets
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


def test_get_request_ticket_list_view_context_data_return_successful(
        client, first_test_admin_user_profile, five_test_tickets
) -> None:

    """
    Test that the user profile is correctly included in the response context.

    - Logs in as an admin user.
    - Sends a GET request to the ticket list endpoint.
    - Asserts that `user_profile` exists in the response context.
    - Ensures the `user_profile` matches the logged-in user's profile.
    """

    admin_user = first_test_admin_user_profile.user
    client.force_login(admin_user)

    response = client.get(path=TICKET_LIST_URL)
    assert 'user_profile' in response.context
    assert response.context['user_profile'] == first_test_admin_user_profile
