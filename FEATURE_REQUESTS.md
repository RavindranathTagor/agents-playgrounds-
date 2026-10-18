# MOVA investigation: GitHub issue drafts

These are copy-ready issue drafts for the two intentional Task Tracker API defects. They have **not** been created on GitHub. Create each issue manually after publishing the repository, or create them in the current GitHub repository if it is already accessible to you.

## Issue 1: Completed tasks are returned as pending by the task-list endpoint

**Type:** Bug

### Description

Completing a task updates its stored status to `completed`, and `GET /tasks/<id>` returns that status correctly. However, `GET /tasks` serializes the same task as `pending`, so clients receive conflicting status values depending on the endpoint used.

### Steps to reproduce

1. Start the API with `python run.py`.
2. Create a task:

   ```bash
   curl -X POST http://127.0.0.1:5000/tasks \
     -H 'Content-Type: application/json' \
     -d '{"title":"Check completion status"}'
   ```

3. Complete the created task (use its returned ID in place of `1`):

   ```bash
   curl -X PATCH http://127.0.0.1:5000/tasks/1/complete
   ```

4. Compare the individual and list responses:

   ```bash
   curl http://127.0.0.1:5000/tasks/1
   curl http://127.0.0.1:5000/tasks
   ```

### Expected behavior

The task-list endpoint returns the task with `"status": "completed"`, matching the completion response and individual task endpoint.

### Actual behavior

`GET /tasks` returns the completed task with `"status": "pending"`.

### Acceptance criteria

- A task completed through `PATCH /tasks/<id>/complete` has status `completed` in `GET /tasks`.
- `GET /tasks/<id>` and `GET /tasks` report the same status for a task.
- The regression test for completed-task list status passes without an expected-failure marker.
- Pending tasks continue to be reported as pending.

## Issue 2: Duplicate task titles are accepted

**Type:** Bug

### Description

The API accepts more than one task with the same title. Duplicate titles should be rejected so clients can rely on task titles being unique.

### Steps to reproduce

1. Start the API with `python run.py`.
2. Submit the same create request twice:

   ```bash
   curl -i -X POST http://127.0.0.1:5000/tasks \
     -H 'Content-Type: application/json' \
     -d '{"title":"Avoid duplicate task"}'
   curl -i -X POST http://127.0.0.1:5000/tasks \
     -H 'Content-Type: application/json' \
     -d '{"title":"Avoid duplicate task"}'
   ```

### Expected behavior

The first request creates the task with `201 Created`. The second request returns `409 Conflict` and a JSON error, for example:

```json
{"error":"a task with this title already exists"}
```

### Actual behavior

Both requests return `201 Created` and create separate tasks with the same title.

### Acceptance criteria

- Creating a task whose title matches an existing task is rejected with `409 Conflict` and a JSON error.
- The original task remains available and no duplicate task is added.
- Duplicate checking uses the title consistently with the API's title handling (surrounding whitespace is stripped on creation).
- The duplicate-title regression test passes without an expected-failure marker.

## Create these issues manually on GitHub

1. Publish the project to the GitHub repository (see the **Publish this project** section in `README.md`) or open the existing repository if you already have access.
2. Open the repository page and select **Issues**. If Issues is disabled, open **Settings → General → Features**, enable **Issues**, then return to the Issues tab.
3. Select **New issue** (or **New issue → Open a blank issue**).
4. Copy the first draft's description into a new issue. Use the heading **Completed tasks are returned as pending by the task-list endpoint** as its title, then select **Submit new issue**.
5. Repeat with the second draft, titled **Duplicate task titles are accepted**.
6. Copy each created issue's URL from the browser and add it to your MOVA investigation notes. This file intentionally contains no issue URLs because neither issue has been created or verified.
