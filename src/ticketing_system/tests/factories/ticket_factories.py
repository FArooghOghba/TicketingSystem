import factory
from factory.django import DjangoModelFactory

from ticketing_system.ticket.models import Ticket
from ticketing_system.tests.factories.profile_factories import UserProfileFactory


class TicketFactory(DjangoModelFactory):

    """
    Factory for creating Ticket instances for testing.

    Attributes:
        - `created_by`: Uses `ProfileFactory` to assign a user profile that creates the ticket.
        - `subject`: Generates a random sentence as the ticket subject.
        - `description`: Generates random text as the ticket description.
    """

    class Meta:
        model = Ticket

    created_by = factory.SubFactory(UserProfileFactory)
    subject = factory.Faker("sentence")
    description = factory.Faker("text")
