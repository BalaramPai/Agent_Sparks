from sqlalchemy.orm import Session

from sparks.persistence.models import Memory
from sparks.persistence.repositories import MemoryRepository


class MemoryService:
    """Application service for durable SPARKS memories."""

    def __init__(self, db: Session):
        self.db = db
        self.memories = MemoryRepository(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def create_memory(
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
        return self.memories.create(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            confidence=confidence,
            source=source,
            embedding=embedding,
            memory_metadata=memory_metadata,
        )

    def get_memory(self, memory_id: int) -> Memory | None:
        return self.memories.get_by_id(memory_id)

    def get_user_memories(self, user_id: int) -> list[Memory]:
        return self.memories.list_by_user(user_id)

    def delete_memory(self, memory: Memory) -> None:
        self.memories.delete(memory)
