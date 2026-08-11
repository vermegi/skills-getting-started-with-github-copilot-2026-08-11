from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)

    # Arrange
    test_client = TestClient(app)

    yield test_client

    # Cleanup: restore mutable global state so tests stay isolated.
    activities.clear()
    activities.update(original_activities)
