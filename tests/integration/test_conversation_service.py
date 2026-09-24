from sparks.persistence.database import SessionLocal
from sparks.persistence.services import ConversationService
from sparks.persistence.models import User


def test_conversation_service_lifecycle():
    with SessionLocal() as db:
        service = ConversationService(db)
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        # Create conversation
        conversation = service.create_conversation(
            user_id=user.id,
            title="Service integration test",
        )

        assert conversation.id is not None

        # Add messages through the service
        user_message = service.add_message(
            conversation_id=conversation.id,
            role="user",
            content="Hello SPARKS",
        )

        assistant_message = service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content="Hello. How can I help?",
        )

        assert user_message.id is not None
        assert assistant_message.id is not None

        # Retrieve conversation
        stored = service.get_conversation(conversation.id)

        assert stored is not None
        assert stored.id == conversation.id
        assert stored.title == "Service integration test"

        # Retrieve messages
        messages = service.get_messages(conversation.id)

        assert len(messages) == 2

        assert messages[0].role == "user"
        assert messages[0].content == "Hello SPARKS"

        assert messages[1].role == "assistant"
        assert messages[1].content == "Hello. How can I help?"

        # Cleanup
        db.delete(stored)
        db.commit()
        
def test_add_message_to_missing_conversation():
    with SessionLocal() as db:
        service = ConversationService(db)

        try:
            service.add_message(
                conversation_id=999999999,
                role="user",
                content="This should fail",
            )
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert str(exc) == (
                "Conversation 999999999 does not exist."
            )

def test_create_conversation_with_message_rolls_back_on_failure():
    with SessionLocal() as db:
        service = ConversationService(db)

        try:
            user = User(
                preferences={},
                settings={},
            )

            db.add(user)
            db.flush()

            conversation = service.conversations.create(
                user_id=user.id,
                title="Should be rolled back",
            )

            # Force a failure before the transaction is committed.
            raise RuntimeError("Simulated transaction failure")

        except RuntimeError:
            service.rollback()

        stored = service.get_conversation(conversation.id)

        assert stored is None