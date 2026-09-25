from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sparks.persistence.database import Base


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    request_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ttft_ms: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    total_latency_ms: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    tokens_per_second: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    vram_mb: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    cpu_percent: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    ram_mb: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    task_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    task: Mapped["Task | None"] = relationship()
