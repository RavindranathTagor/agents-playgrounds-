# Task Tracker API

A small, beginner-friendly task tracker built with Python and Flask. It includes a visual task dashboard at `/` and a JSON REST API at `/tasks`. Tasks are stored in memory, so data resets when the application restarts.

> **MOVA investigation demo:** Two intentional defects are present and documented: the list response reports completed tasks as pending, and duplicate titles are accepted. Regression tests are marked as expected failures so the normal test suite remains green. See [Known demo bugs](#known-demo-bugs).

Two copy-ready GitHub issue drafts, with reproduction steps and acceptance criteria, are in [`FEATURE_REQUESTS.md`](FEATURE_REQUESTS.md). No issues are created automatically; use the manual steps in that file when you are ready to open them.

## Setup

Requires Python 3.9 or newer.

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```bash
python run.py
```

The app listens at `http://127.0.0.1:5000`. Open that address for the visual task dashboard. The REST endpoint list is at `http://127.0.0.1:5000/api`. For development, Flask debug mode is enabled by the runner. You can also set `FLASK_APP=run.py` and use `flask run`.

## API

All request and response bodies are JSON. A task has this shape:

```json
{
  "id": 1,
  "title": "Write project README",
  "description": "Document setup and endpoints",
  "status": "pending",
  "created_at": "2026-10-18T12:30:00+00:00"
}
```

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `POST` | `/tasks` | Create a task | `201 Created` |
| `GET` | `/tasks` | List all tasks | `200 OK` |
| `GET` | `/tasks/<id>` | Retrieve one task | `200 OK` |
| `PUT` | `/tasks/<id>` | Update title and/or description | `200 OK` |
| `PATCH` | `/tasks/<id>/complete` | Mark a task complete | `200 OK` |
| `DELETE` | `/tasks/<id>` | Delete a task | `204 No Content` |

The dashboard lets you add tasks, view all/to-do/completed filters, edit task details, mark tasks complete, and delete tasks. It uses the same API documented below.

Creation requires a non-empty string `title`. `description` is optional and defaults to an empty string. Updates accept either or both fields. Unknown fields, wrong JSON types, missing titles, and blank titles return a JSON error with `400 Bad Request`; nonexistent task IDs return `404 Not Found`.

### Example requests

Create a task:

```bash
curl -i -X POST http://127.0.0.1:5000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Write project README","description":"Document the API"}'
```

List tasks:

```bash
curl http://127.0.0.1:5000/tasks
```

Update, complete, and delete task `1`:

```bash
curl -X PUT http://127.0.0.1:5000/tasks/1 \
  -H 'Content-Type: application/json' -d '{"title":"Polish README"}'
curl -X PATCH http://127.0.0.1:5000/tasks/1/complete
curl -i -X DELETE http://127.0.0.1:5000/tasks/1
```

Retrieve a task and submit invalid input:

```bash
curl -i http://127.0.0.1:5000/tasks/1
curl -i -X POST http://127.0.0.1:5000/tasks \
  -H 'Content-Type: application/json' -d '{"description":"Missing title"}'
```

The second request returns `400 Bad Request` and `{"error":"title is required"}`. Requests for missing task IDs return `404 Not Found` with `{"error":"task not found"}`.

Errors use a consistent format, for example `{"error":"title is required"}`.

## Tests

```bash
python -m pytest -v
```

Expected result: normal functionality tests pass; the two intentional bug regression cases show as `XFAIL`.

## Known demo bugs

These defects are intentionally retained for a MOVA investigation demo and have regression tests in `tests/test_demo_bugs.py`:

1. **Completed status in list:** completing a task stores `completed`, and retrieving that task returns `completed`, but `GET /tasks` serializes completed tasks as `pending`. The dashboard applies the completion response immediately, so the task appears complete until a reload fetches the buggy list response. The regression test records the expected correct API behavior (`XFAIL`).
2. **Duplicate titles:** task creation accepts a title already used by another task; the intended API behavior is `409 Conflict` with a JSON error. The regression test records that expectation (`XFAIL`).

`pytest.mark.xfail(strict=True)` keeps the suite green while ensuring either defect unexpectedly disappearing is visible as an `XPASS` failure, prompting removal or revision of the demo marker.

## Demonstrate with MOVA

This project exposes a local HTTP API that MOVA can investigate. Start it in a terminal:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Use `http://127.0.0.1:5000` as the API base URL in MOVA when it can access services on your machine. If MOVA is running in a separate container or remote environment, use a host address reachable from that environment instead; `127.0.0.1` always refers to the caller itself.

Reproduce the completed-task list bug in a second terminal:

```bash
curl -X POST http://127.0.0.1:5000/tasks \
  -H 'Content-Type: application/json' -d '{"title":"MOVA completion demo"}'
curl -X PATCH http://127.0.0.1:5000/tasks/1/complete
curl http://127.0.0.1:5000/tasks
```

The completion response says `completed`, while the list response incorrectly says `pending`. To reproduce the duplicate-title bug, submit the same `POST /tasks` request twice; both requests currently return `201 Created`. Restarting the server clears the in-memory tasks. Run `python -m pytest -v` to see both bug regressions as `XFAIL`.

## Publish this project

This workspace is on branch `main` and already has an `origin` remote configured. To publish the current project files to that existing GitHub repository, review the staged changes, then run:

```bash
git status --short
git add .gitignore README.md FEATURE_REQUESTS.md requirements.txt run.py task_tracker tests
git diff --cached --check
git commit -m "Prepare Task Tracker API MOVA demo"
git push -u origin main
```

Authenticate with GitHub if prompted. The `git add` command stages only the Task Tracker project files shown above.
