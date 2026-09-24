from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models import Memory


class MemoryRepository:
    """Persistence operations for durable SPARKS memories."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        memory_type: str,
        content: str,
        importance: float,
        confidence: float,
        source: str | None = None,
        embedding: list | None = None,
        memory_metadata: dict | None = None,
    ) -> Memory:
        memory = Memory(
            user_id=user_id,
            type=memory_type,
            content=content,
            importance=importance,
            confidence=confidence,
            source=source,
            embedding=embedding,
            memory_metadata=memory_metadata or {},
        )

        self.db.add(memory)
        self.db.flush()

        return memory

    def get_by_id(self, memory_id: int) -> Memory | None:
        statement = select(Memory).where(Memory.id == memory_id)
        return self.db.scalar(statement)

    def list_by_user(self, user_id: int) -> list[Memory]:
        statement = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at, Memory.id)
        )

        return list(self.db.scalars(statement).all())

    def delete(self, memory: Memory) -> None:
        self.db.delete(memory)
