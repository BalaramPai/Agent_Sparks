from sparks.persistence.database import SessionLocal
from sparks.persistence.models import User
from sparks.persistence.services import MemoryService


def test_memory_service_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = MemoryService(db)

        memory = service.create_memory(
            user_id=user.id,
            memory_type="PREFERENCE",
            content="User prefers dark mode.",
            importance=0.9,
            confidence=0.95,
            source="conversation",
            memory_metadata={
                "category": "ui",
            },
        )

        service.commit()

        assert memory.id is not None

        loaded_memory = service.get_memory(memory.id)

        assert loaded_memory is not None
        assert loaded_memory.id == memory.id
        assert loaded_memory.user_id == user.id
        assert loaded_memory.type == "PREFERENCE"
        assert loaded_memory.content == "User prefers dark mode."
        assert loaded_memory.importance == 0.9
        assert loaded_memory.confidence == 0.95
        assert loaded_memory.memory_metadata == {
            "category": "ui",
        }


def test_memory_service_get_user_memories():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = MemoryService(db)

        service.create_memory(
            user_id=user.id,
            memory_type="FACT",
            content="User is an engineering student.",
            importance=0.8,
            confidence=0.95,
        )

        service.create_memory(
            user_id=user.id,
            memory_type="PROJECT",
            content="User is building SPARKS.",
            importance=1.0,
            confidence=0.99,
        )

        service.commit()

        memories = service.get_user_memories(user.id)

        assert len(memories) == 2
        assert memories[0].type == "FACT"
        assert memories[1].type == "PROJECT"


def test_memory_service_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = MemoryService(db)

        memory = service.create_memory(
            user_id=user.id,
            memory_type="FACT",
            content="Temporary memory.",
            importance=0.5,
            confidence=0.8,
        )

        service.commit()

        memory_id = memory.id

        service.delete_memory(memory)
        service.commit()

        assert service.get_memory(memory_id) is None


def test_memory_service_rollback():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = MemoryService(db)

        service.create_memory(
            user_id=user.id,
            memory_type="FACT",
            content="Rollback test.",
            importance=0.5,
            confidence=0.8,
        )

        service.rollback()

        assert service.get_user_memories(user.id) == []
