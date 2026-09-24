from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models import Message


class MessageRepository:
    """Database operations for messages."""

    def __init__(self, db: Session):
        self.db = db

    def create(
    self,
    conversation_id: int,
    role: str,
    content: str,
    ) -> Message:
        """Create a message without committing."""

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.flush()

        return message

    def get_by_id(self, message_id: int) -> Message | None:
        """Return a message by ID."""

        statement = select(Message).where(
            Message.id == message_id
        )

        return self.db.scalar(statement)

    def list_by_conversation(
        self,
        conversation_id: int,
    ) -> list[Message]:
        """Return messages belonging to a conversation."""

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )

        return list(self.db.scalars(statement).all())

    def delete(self, message: Message) -> None:
        """Mark a message for deletion."""

        self.db.delete(message)