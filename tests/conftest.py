import pytest

from task_tracker import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()
