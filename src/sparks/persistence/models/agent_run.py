from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sparks.persistence.database import Base


class AgentRunStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[AgentRunStatus] = mapped_column(
        String(20),
        default=AgentRunStatus.RUNNING,
        nullable=False,
        index=True,
    )

    tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    latency: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    task: Mapped["Task"] = relationship()
