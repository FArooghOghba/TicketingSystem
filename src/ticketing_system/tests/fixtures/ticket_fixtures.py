from typing import Any, Generator, TYPE_CHECKING

import pytest

from ticketing_system.tests.factories.ticket_factories import TicketFactory
from ticketing_system.ticket.models import TicketStatus

if TYPE_CHECKING:
    from ticketing_system.ticket.models import Ticket


@pytest.fixture
def first_test_pending_ticket() -> 'Ticket':

    """
    Fixture to create a pending ticket.

    Returns:
        - A `Ticket` instance with status set to `PENDING`.
    """

    return TicketFactory(status=TicketStatus.PENDING)


@pytest.fixture
def first_test_in_progress_ticket() -> 'Ticket':

    """
    Fixture to create an in-progress ticket.

    Returns:
        - A `Ticket` instance with status set to `IN_PROGRESS`.
    """

    return TicketFactory(status=TicketStatus.IN_PROGRESS)


@pytest.fixture
def first_test_closed_ticket() -> 'Ticket':

    """
    Fixture to create a closed ticket.

    Returns:
        - A `Ticket` instance with status set to `CLOSED`.
    """

    return TicketFactory(status=TicketStatus.CLOSED)


@pytest.fixture
def five_test_tickets() -> Generator[Any, Any, None]:

    """
    Fixture that creates a batch of five test tickets.

    This fixture uses the TicketFactory to create a batch of five test tickets
    and yields the created tickets. The test tickets can be used in tests that
    require multiple movie objects.

    :return: A list of five test ticket objects.
    """

    test_tickets = TicketFactory.create_batch(5)
    yield test_tickets
