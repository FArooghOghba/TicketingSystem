import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from ticketing_system.users.models import Profile
from ticketing_system.users.models import UserRole


pytestmark = pytest.mark.django_db

User = get_user_model()


def test_create_customer_user_profile_return_successful(first_test_user: 'User') -> None:

    """
    Ensure a profile is created successfully when linked to a user.

    This test verifies that:
    - A profile is correctly associated with a user.
    - Default values for ticket counters are set to zero.
    - The string representation of the profile includes the user's email and role.
    - The default role is 'Customer', and it returns the correct display value.
    """

    profile = Profile.objects.create(user=first_test_user)

    assert profile.user == first_test_user

    assert profile.created_ticket_count == 0
    assert profile.pending_ticket_count == 0
    assert profile.in_progress_ticket_count == 0
    assert profile.closed_ticket_count == 0

    assert profile.role == UserRole.CUSTOMER
    assert profile.get_role_display() == "Customer"

    profile_repr = f"Profile of {profile.user.email} with Role {profile.get_role_display()}"
    assert str(profile) == profile_repr


def test_change_user_profile_role_return_successful(
        first_test_user_profile: 'Profile'
) -> None:

    """
    Ensure a user's role can be successfully updated.

    This test checks that:
    - The role field can be changed to a valid value.
    - The update is correctly saved and reflected in the database.
    """

    first_test_user_profile.role = UserRole.ADMIN
    first_test_user_profile.full_clean()

    first_test_user_profile.save()
    first_test_user_profile.refresh_from_db()
    assert first_test_user_profile.role == UserRole.ADMIN


def test_change_user_profile_role_with_invalid_data_return_error(
        first_test_user_profile: 'Profile'
) -> None:

    """
    Ensure invalid roles are not accepted.

    This test verifies that:
    - Assigning an invalid role (not in the choices) raises a
    ValidationError.
    """

    first_test_user_profile.role = "invalid_role"
    with pytest.raises(ValidationError):
        first_test_user_profile.full_clean()


def test_deletion_profile_after_user_delete_return_error(
        first_test_user: 'User'
) -> None:

    """
    Ensure a profile is deleted when the associated user is deleted.

    This test verifies that:
    - Deleting a user results in the automatic deletion of their
    associated profile due to the OneToOneField
    `on_delete=models.CASCADE` setting.
    - Attempting to retrieve the profile after user deletion
    raises a Profile.DoesNotExist exception.
    """

    profile = Profile.objects.create(user=first_test_user)
    first_test_user.delete()

    with pytest.raises(Profile.DoesNotExist):
        Profile.objects.get(id=profile.id)


def test_create_user_profile_with_existed_user_return_error(
        first_test_user: 'User'
) -> None:

    """
    Ensure a user cannot have more than one profile.

    This test verifies that:
    - Attempting to create a second profile for the same
    user raises an IntegrityError.
    - The one-to-one relationship constraint between User
    and Profile is enforced.
    """

    Profile.objects.create(user=first_test_user)

    with pytest.raises(IntegrityError):
        Profile.objects.create(user=first_test_user)
