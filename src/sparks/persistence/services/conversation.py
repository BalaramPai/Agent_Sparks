from sqlalchemy.orm import Session

from sparks.persistence.models import Conversation, Message
from sparks.persistence.repositories import (
    ConversationRepository,
    MessageRepository,
)


class ConversationService:
    """Application-level operations for conversations."""

    def __init__(self, db: Session):
        self.db = db
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)

    def commit(self) -> None:
        """Commit the current transaction."""

        self.db.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""

        self.db.rollback()

    def create_conversation(
    self,
    user_id: int,
    title: str | None = None,
    ) -> Conversation:
        return self.conversations.create(
            user_id=user_id,
            title=title,
        )

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> Message:
        """Add a message to an existing conversation."""

        conversation = self.conversations.get_by_id(conversation_id)

        if conversation is None:
            raise ValueError(
                f"Conversation {conversation_id} does not exist."
            )

        return self.messages.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

    def get_conversation(
        self,
        conversation_id: int,
    ) -> Conversation | None:
        """Retrieve a conversation."""

        return self.conversations.get_by_id(conversation_id)

    def get_messages(
        self,
        conversation_id: int,
    ) -> list[Message]:
        """Retrieve all messages in a conversation."""

        return self.messages.list_by_conversation(
            conversation_id,
        )

    def create_conversation_with_message(
    self,
    user_id: int,
    title: str | None,
    role: str,
    content: str,
    ) -> tuple[Conversation, Message]:
        try:
            conversation = self.conversations.create(
                user_id=user_id,
                title=title,
            )

            message = self.messages.create(
                conversation_id=conversation.id,
                role=role,
                content=content,
            )

            self.commit()

            return conversation, message

        except Exception:
            self.rollback()
            raise