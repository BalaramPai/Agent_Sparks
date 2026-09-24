from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sparks.persistence.database import Base

if TYPE_CHECKING:
    from sparks.persistence.models.conversation import Conversation
    from sparks.persistence.models.user import User


class Session(Base):
    """Persistent SPARKS runtime session."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    device_info: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    session_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="sessions",
    )
    
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="session",
    )