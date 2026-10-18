"""HTTP routes and request validation for task resources."""

from flask import Blueprint, current_app, jsonify, render_template, request

tasks_blueprint = Blueprint("tasks", __name__)
ALLOWED_FIELDS = {"title", "description"}


def _store():
    return current_app.extensions["task_store"]


def _error(message, status_code):
    return jsonify({"error": message}), status_code


@tasks_blueprint.get("/")
def task_page():
    """Render the task dashboard for browser visitors."""
    return render_template("index.html")


@tasks_blueprint.get("/api")
def api_index():
    """List API endpoints for clients that want the API index."""
    return jsonify(
        {
            "name": "Task Tracker API",
            "endpoints": {
                "create_task": "POST /tasks",
                "list_tasks": "GET /tasks",
                "get_task": "GET /tasks/<id>",
                "update_task": "PUT /tasks/<id>",
                "complete_task": "PATCH /tasks/<id>/complete",
                "delete_task": "DELETE /tasks/<id>",
            },
        }
    ), 200


def _json_object():
    if not request.is_json:
        return None, (jsonify({"error": "Content-Type must be application/json"}), 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "request body must be a JSON object"}), 400)
    return data, None


def _validate_fields(data, require_title=False):
    unknown = set(data) - ALLOWED_FIELDS
    if unknown:
        return f"unknown field: {sorted(unknown)[0]}"
    if require_title and "title" not in data:
        return "title is required"
    if "title" in data and (not isinstance(data["title"], str) or not data["title"].strip()):
        return "title must be a non-empty string"
    if "description" in data and not isinstance(data["description"], str):
        return "description must be a string"
    if not data:
        return "at least one field is required"
    return None


def _task_or_404(task_id):
    task = _store().get(task_id)
    return task


@tasks_blueprint.post("/tasks")
def create_task():
    data, error = _json_object()
    if error:
        return error
    message = _validate_fields(data, require_title=True)
    if message:
        return _error(message, 400)

    # Demo bug: there is intentionally no duplicate-title check here.
    task = _store().create(data["title"].strip(), data.get("description", ""))
    return jsonify(task.to_dict()), 201


@tasks_blueprint.get("/tasks")
def list_tasks():
    tasks = [task.to_dict(for_list=True) for task in _store().list()]
    return jsonify(tasks), 200


@tasks_blueprint.get("/tasks/<int:task_id>")
def get_task(task_id):
    task = _task_or_404(task_id)
    if task is None:
        return _error("task not found", 404)
    return jsonify(task.to_dict()), 200


@tasks_blueprint.put("/tasks/<int:task_id>")
def update_task(task_id):
    task = _task_or_404(task_id)
    if task is None:
        return _error("task not found", 404)
    data, error = _json_object()
    if error:
        return error
    message = _validate_fields(data)
    if message:
        return _error(message, 400)
    if "title" in data:
        task.title = data["title"].strip()
    if "description" in data:
        task.description = data["description"]
    return jsonify(task.to_dict()), 200


@tasks_blueprint.patch("/tasks/<int:task_id>/complete")
def complete_task(task_id):
    task = _task_or_404(task_id)
    if task is None:
        return _error("task not found", 404)
    task.status = "completed"
    return jsonify(task.to_dict()), 200


@tasks_blueprint.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    if _store().delete(task_id) is None:
        return _error("task not found", 404)
    return "", 204
