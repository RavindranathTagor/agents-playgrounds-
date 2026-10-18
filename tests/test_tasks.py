"""Tests for expected Task Tracker API behavior."""


def create_task(client, title="Prepare demo", description="Get ready"):
    return client.post("/tasks", json={"title": title, "description": description})


def test_create_and_retrieve_task(client):
    response = create_task(client)
    assert response.status_code == 201
    task = response.get_json()
    assert task["id"] == 1
    assert task["title"] == "Prepare demo"
    assert task["description"] == "Get ready"
    assert task["status"] == "pending"
    assert task["created_at"]

    retrieved = client.get("/tasks/1")
    assert retrieved.status_code == 200
    assert retrieved.get_json() == task


def test_list_tasks(client):
    create_task(client)
    response = client.get("/tasks")
    assert response.status_code == 200
    assert [task["title"] for task in response.get_json()] == ["Prepare demo"]


def test_home_page_renders_task_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
    assert b"Your tasks," in response.data
    assert b"in motion." in response.data


def test_create_form_resets_and_refreshes_dashboard_after_success(client):
    page = client.get("/").get_data(as_text=True)
    handler = page.split("createForm.addEventListener('submit'", 1)[1].split(
        "document.querySelector('#focusAdd')", 1
    )[0]

    assert "const form = new FormData(createForm)" in handler
    assert "event.currentTarget.reset()" not in handler
    assert handler.index("await api('/tasks'") < handler.index("createForm.reset()")
    assert handler.index("createForm.reset()") < handler.index("await loadTasks()")


def test_dashboard_uses_completion_response_for_immediate_status(client):
    page = client.get("/").get_data(as_text=True)
    handler = page.split("if (button.dataset.action === 'complete')", 1)[1].split(
        "} else if (button.dataset.action === 'delete')", 1
    )[0]

    assert "const completedTask = await api(`/tasks/${id}/complete`" in handler
    assert "tasks = tasks.map((item) => item.id === completedTask.id ? completedTask : item)" in handler
    assert "renderTasks()" in handler
    assert "await loadTasks()" not in handler


def test_api_index_lists_available_endpoints(client):
    response = client.get("/api")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Task Tracker API"
    assert response.get_json()["endpoints"]["list_tasks"] == "GET /tasks"


def test_update_task_fields(client):
    create_task(client)
    response = client.put("/tasks/1", json={"title": "Updated", "description": "Details"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "Updated"
    assert response.get_json()["description"] == "Details"


def test_complete_task_and_retrieve(client):
    create_task(client)
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    assert response.get_json()["status"] == "completed"
    assert client.get("/tasks/1").get_json()["status"] == "completed"


def test_delete_task(client):
    create_task(client)
    assert client.delete("/tasks/1").status_code == 204
    missing = client.get("/tasks/1")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "task not found"}


def test_missing_or_invalid_title_returns_json_error(client):
    missing = client.post("/tasks", json={"description": "No title"})
    assert missing.status_code == 400
    assert missing.get_json() == {"error": "title is required"}

    blank = client.post("/tasks", json={"title": "  "})
    assert blank.status_code == 400
    assert blank.get_json() == {"error": "title must be a non-empty string"}


def test_invalid_json_shape_and_field_types(client):
    wrong_type = client.post("/tasks", json=["not", "an", "object"])
    assert wrong_type.status_code == 400
    assert "error" in wrong_type.get_json()

    invalid_description = client.post("/tasks", json={"title": "Valid", "description": 3})
    assert invalid_description.status_code == 400
    assert invalid_description.get_json() == {"error": "description must be a string"}

    invalid_title = client.post("/tasks", json={"title": 42})
    assert invalid_title.status_code == 400
    assert invalid_title.get_json() == {"error": "title must be a non-empty string"}

    unknown_field = client.post("/tasks", json={"title": "Valid", "priority": "high"})
    assert unknown_field.status_code == 400
    assert unknown_field.get_json() == {"error": "unknown field: priority"}

    malformed = client.post("/tasks", data="{bad json", content_type="application/json")
    assert malformed.status_code == 400
    assert malformed.get_json() == {"error": "request body must be a JSON object"}


def test_not_found_responses(client):
    assert client.get("/tasks/99").status_code == 404
    assert client.put("/tasks/99", json={"title": "Changed"}).status_code == 404
    assert client.patch("/tasks/99/complete").status_code == 404
    assert client.delete("/tasks/99").status_code == 404


def test_empty_and_invalid_content_type(client):
    empty = client.post("/tasks", json={})
    assert empty.status_code == 400
    assert empty.get_json() == {"error": "title is required"}

    invalid_type = client.post("/tasks", data="title=hello", content_type="text/plain")
    assert invalid_type.status_code == 400
    assert invalid_type.get_json() == {"error": "Content-Type must be application/json"}


def test_unknown_resource_and_method_errors_are_json(client):
    missing = client.get("/not-a-route")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "resource not found"}

    wrong_method = client.post("/tasks/1/complete")
    assert wrong_method.status_code == 405
    assert wrong_method.get_json() == {"error": "method not allowed"}
