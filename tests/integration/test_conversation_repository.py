from sparks.persistence.database import SessionLocal
from sparks.persistence.models import User
from sparks.persistence.repositories import ConversationRepository


def test_conversation_repository_create_and_get():
    with SessionLocal() as db:
        repository = ConversationRepository(db)

        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        conversation = repository.create(
            user_id=user.id,
            title="Repository test",
        )

        assert conversation.id is not None
        assert conversation.title == "Repository test"
        assert conversation.user_id == user.id

        stored = repository.get_by_id(conversation.id)

        assert stored is not None
        assert stored.id == conversation.id
        assert stored.title == "Repository test"
        assert stored.user_id == user.id

        repository.delete(stored)
        db.commit()

        assert repository.get_by_id(conversation.id) is None