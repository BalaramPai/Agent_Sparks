from sparks.persistence.database import SessionLocal
from sparks.persistence.models import User
from sparks.persistence.repositories import MemoryRepository


def test_memory_repository_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = MemoryRepository(db)

        memory = repository.create(
            user_id=user.id,
            memory_type="FACT",
            content="User prefers dark mode.",
            importance=0.8,
            confidence=0.95,
            source="conversation",
            embedding=[0.1, 0.2, 0.3],
            memory_metadata={"test": True},
        )

        db.commit()

        assert memory.id is not None
        assert memory.user_id == user.id
        assert memory.type == "FACT"
        assert memory.content == "User prefers dark mode."
        assert memory.importance == 0.8
        assert memory.confidence == 0.95
        assert memory.source == "conversation"
        assert memory.embedding == [0.1, 0.2, 0.3]
        assert memory.memory_metadata == {"test": True}

        loaded_memory = repository.get_by_id(memory.id)

        assert loaded_memory is not None
        assert loaded_memory.id == memory.id
        assert loaded_memory.content == "User prefers dark mode."


def test_memory_repository_list_by_user():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = MemoryRepository(db)

        repository.create(
            user_id=user.id,
            memory_type="FACT",
            content="Memory one",
            importance=0.5,
            confidence=0.9,
        )

        repository.create(
            user_id=user.id,
            memory_type="PREFERENCE",
            content="Memory two",
            importance=0.7,
            confidence=0.8,
        )

        db.commit()

        memories = repository.list_by_user(user.id)

        assert len(memories) == 2
        assert memories[0].content == "Memory one"
        assert memories[1].content == "Memory two"


def test_memory_repository_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = MemoryRepository(db)

        memory = repository.create(
            user_id=user.id,
            memory_type="FACT",
            content="Temporary memory",
            importance=0.4,
            confidence=0.9,
        )

        db.commit()

        memory_id = memory.id

        repository.delete(memory)
        db.commit()

        assert repository.get_by_id(memory_id) is None
