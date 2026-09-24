from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str | None = None,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)
        self.db.flush()

        return conversation

    def get_by_id(self, conversation_id: int) -> Conversation | None:
        statement = select(Conversation).where(
            Conversation.id == conversation_id
        )

        return self.db.scalar(statement)

    def delete(self, conversation: Conversation) -> None:
        self.db.delete(conversation)