"""Task data object and JSON serialization."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    status: str = "pending"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self, for_list=False):
        """Return JSON-ready task data.

        Demo bug: list serialization incorrectly maps completed to pending.
        Single-task retrieval still reports the stored status correctly.
        """
        status = "pending" if for_list and self.status == "completed" else self.status
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": status,
            "created_at": self.created_at,
        }
