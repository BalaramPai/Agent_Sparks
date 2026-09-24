from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Conversation, Message, User


def test_conversation_message_lifecycle():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        conversation = Conversation(
            user_id=user.id,
            title="SPARKS conversation test",
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        conversation_id = conversation.id

        # Add messages
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content="Hello SPARKS",
        )

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content="Hello. I am SPARKS.",
        )

        db.add_all([user_message, assistant_message])
        db.commit()

        # Reload conversation and verify relationship
        stored = db.get(Conversation, conversation_id)

        assert stored is not None
        assert len(stored.messages) == 2

        assert stored.messages[0].role == "user"
        assert stored.messages[0].content == "Hello SPARKS"

        assert stored.messages[1].role == "assistant"
        assert stored.messages[1].content == "Hello. I am SPARKS."

        # Delete conversation
        db.delete(stored)
        db.commit()

        # Verify conversation and messages were deleted
        assert db.get(Conversation, conversation_id) is None

        remaining_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .all()
        )

        assert remaining_messages == []