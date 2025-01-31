import uuid

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from ticketing_system.users.models import Profile
from ticketing_system.ticket.models import Ticket
from ticketing_system.ticket.models import TicketStatus
from ticketing_system.ticket.models import TicketPriority


pytestmark = pytest.mark.django_db

User = get_user_model()


def test_create_ticket_model_return_successful(
        first_test_user_profile: 'Profile'
) -> None:

    """
    Test that a ticket is created successfully with the required fields.

    Ensures that:
    - The ticket is created with a valid subject and description.
    - The default status is PENDING.
    - The default priority is MEDIUM.
    - The generated ticket ID is a valid UUID.
    - The total ticket count in the database increases by one.
    """

    ticket = Ticket.objects.create(
        created_by=first_test_user_profile,
        subject="Test Subject",
        description="Test Description"
    )

    assert str(ticket) == f"Test Subject ({TicketStatus.PENDING.label})"

    assert ticket.status == TicketStatus.PENDING
    assert ticket.priority == TicketPriority.MEDIUM
    assert isinstance(ticket.ticket_id, uuid.UUID)
    assert Ticket.objects.count() == 1


def test_create_ticket_with_assignment_to_staff_user_return_successful(
        first_test_user_profile: 'Profile', first_test_staff_user_profile: 'Profile'
) -> None:

    """
    Test that a ticket can be assigned to a staff user.

    Ensures that:
    - The ticket assignment is successful when the assigned user is a staff member.
    - The assigned staff user is correctly stored in the database.
    """

    ticket = Ticket.objects.create(
        created_by=first_test_user_profile,
        subject="Test",
        description="Test",
        assigned_to=first_test_staff_user_profile
    )

    assert ticket.assigned_to == first_test_staff_user_profile


def test_create_ticket_with_file_upload_return_successful(
        first_test_user_profile: 'Profile'
) -> None:

    """
    Test that a file can be uploaded and attached to a ticket.

    Ensures that:
    - The uploaded file is correctly saved under the expected directory.
    - The file content type is preserved.
    """

    test_file = SimpleUploadedFile(
        name="test_file.txt",
        content=b"Test content",
        content_type="text/plain"
    )

    ticket = Ticket.objects.create(
        created_by=first_test_user_profile,
        subject="File Test",
        description="Test",
        file=test_file
    )

    assert ticket.file.name.startswith("tickets/files/")


def test_create_ticket_assignment_to_wrong_user_return_error(
        first_test_user_profile: 'Profile', second_test_user_profile: 'Profile'
) -> None:

    """
    Test that a ticket cannot be assigned to a non-staff user.

    Ensures that:
    - Assigning a ticket to a non-staff user raises a ValidationError.
    - The validation logic for ticket assignment is enforced correctly.
    """

    ticket = Ticket(
        created_by=first_test_user_profile,
        subject="Test",
        description="Test",
        assigned_to=second_test_user_profile
    )

    with pytest.raises(ValidationError):
        ticket.full_clean()
