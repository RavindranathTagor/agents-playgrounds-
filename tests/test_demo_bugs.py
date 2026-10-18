"""Expected-failure regressions for the two intentional MOVA demo bugs."""

import pytest


@pytest.mark.xfail(strict=True, reason="MOVA demo bug: list serializer reports completed tasks as pending")
def test_completed_task_is_reported_completed_in_list(client):
    client.post("/tasks", json={"title": "Finish demo"})
    client.patch("/tasks/1/complete")

    listed = client.get("/tasks").get_json()
    assert listed[0]["status"] == "completed"


@pytest.mark.xfail(strict=True, reason="MOVA demo bug: duplicate task titles are accepted")
def test_duplicate_title_is_rejected(client):
    first = client.post("/tasks", json={"title": "Unique title"})
    duplicate = client.post("/tasks", json={"title": "Unique title"})

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.get_json() == {"error": "a task with this title already exists"}
