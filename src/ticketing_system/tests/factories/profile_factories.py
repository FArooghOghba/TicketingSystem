from factory import SubFactory
from factory.django import DjangoModelFactory

from ticketing_system.users.models import Profile
from ticketing_system.tests.factories.user_factories import BaseUserFactory


class UserProfileFactory(DjangoModelFactory):

    """
    Factory for creating test Profile instances.

    Uses:
    - Automatically generates a linked User instance via BaseUserFactory.
    - Sets default values for Profile fields.
    """

    class Meta:
        model = Profile

    user = SubFactory(BaseUserFactory)
