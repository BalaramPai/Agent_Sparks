from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RuntimeStatus(str, Enum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class RuntimeState:
    """
    Hot in-memory state for the SPARKS runtime.

    This is intentionally ephemeral.
    Durable state will eventually be persisted through PostgreSQL.
    """

    status: RuntimeStatus = RuntimeStatus.STOPPED

    started_at: datetime | None = None
    stopped_at: datetime | None = None

    active_task_id: str | None = None
    active_agent: str | None = None

    context: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        self.status = RuntimeStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self.stopped_at = None

    def stop(self) -> None:
        self.status = RuntimeStatus.STOPPED
        self.stopped_at = datetime.now(timezone.utc)
        self.active_task_id = None
        self.active_agent = None

    def set_context(self, key: str, value: Any) -> None:
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)

    def clear_context(self) -> None:
        self.context.clear()

    def set_task(self, task_id: str | None) -> None:
        self.active_task_id = task_id

    def set_agent(self, agent: str | None) -> None:
        self.active_agent = agent

    @property
    def is_running(self) -> bool:
        return self.status == RuntimeStatus.RUNNING