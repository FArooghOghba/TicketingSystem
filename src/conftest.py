"""
Conf test for tests
"""
from datetime import datetime
from typing import Generator

import pytest
from django.test import Client


@pytest.fixture
def client() -> 'Client':

    """
    Fixture for creating an instance of the Django Client.
    :return: Client()
    """

    return Client()


@pytest.fixture(autouse=True)
def time_tracker() -> Generator[None, None, None]:

    """
    Fixture for tracking the runtime of a test or a block of code.

    This fixture captures the start time before executing the test or
    the block of code, and calculates the elapsed time after the execution.
    It then prints the runtime in seconds.
    :return: runtime for how long it has taken to run the test.
    """

    tick = datetime.now()
    yield

    tock = datetime.now()
    diff = tock - tick
    print(f'\n runtime: {diff.total_seconds()}')


from ticketing_system.tests.fixtures.user_fixtures import *  # noqa
from ticketing_system.tests.fixtures.email_fixtures import *  # noqa
