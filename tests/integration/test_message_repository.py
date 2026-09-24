from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Conversation, User
from sparks.persistence.repositories import MessageRepository


def test_message_repository_create_and_list():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        conversation = Conversation(
            user_id=user.id,
            title="Message repository test",
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        repository = MessageRepository(db)

        first = repository.create(
            conversation_id=conversation.id,
            role="user",
            content="Hello SPARKS",
        )

        second = repository.create(
            conversation_id=conversation.id,
            role="assistant",
            content="Hello. How can I help?",
        )

        assert first.id is not None
        assert second.id is not None

        messages = repository.list_by_conversation(
            conversation.id,
        )

        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello SPARKS"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hello. How can I help?"

        stored = repository.get_by_id(first.id)

        assert stored is not None
        assert stored.id == first.id

        repository.delete(stored)
        db.commit()

        assert repository.get_by_id(first.id) is None

        db.delete(conversation)
        db.commit()