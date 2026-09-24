from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sparks.persistence.database import Base

if TYPE_CHECKING:
    from sparks.persistence.models.conversation import Conversation


class User(Base):
    """Persistent SPARKS user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    preferences: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    settings: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )