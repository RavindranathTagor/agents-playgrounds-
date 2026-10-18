"""Simple in-memory storage for tasks."""

from task_tracker.models import Task


class TaskStore:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def create(self, title, description=""):
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id):
        return self._tasks.get(task_id)

    def list(self):
        return list(self._tasks.values())

    def delete(self, task_id):
        return self._tasks.pop(task_id, None)
