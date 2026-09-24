from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sparks.persistence.database import Base

if TYPE_CHECKING:
    from sparks.persistence.models.session import Session


class ContextSnapshot(Base):
    """Durable snapshot of meaningful SPARKS runtime context."""

    __tablename__ = "context_snapshots"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    active_application: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    active_project: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    active_task: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    relevant_context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float] = mapped_column(
        nullable=False,
    )

    snapshot_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    session: Mapped["Session"] = relationship()
