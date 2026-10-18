"""Flask application factory for the Task Tracker API."""

from flask import Flask

from task_tracker.routes import tasks_blueprint
from task_tracker.store import TaskStore


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(JSON_SORT_KEYS=False)
    if test_config:
        app.config.update(test_config)

    # Each application instance gets a fresh, in-memory task store.
    app.extensions["task_store"] = TaskStore()
    app.register_blueprint(tasks_blueprint)

    @app.errorhandler(404)
    def not_found(_error):
        return {"error": "resource not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return {"error": "method not allowed"}, 405

    return app
