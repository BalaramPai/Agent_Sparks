from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Session, User
from sparks.persistence.services import ContextSnapshotService


def test_context_snapshot_service_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        session = Session(
            user_id=user.id,
            device_info={"platform": "Windows"},
            session_metadata={},
        )

        db.add(session)
        db.flush()

        service = ContextSnapshotService(db)

        snapshot = service.create(
            session_id=session.id,
            active_application="VS Code",
            active_project="SPARKS",
            active_task="Phase 3",
            relevant_context="Testing context persistence.",
            confidence=0.95,
            snapshot_metadata={"source": "service-test"},
        )

        assert snapshot.id is not None
        assert snapshot.session_id == session.id
        assert snapshot.active_application == "VS Code"
        assert snapshot.active_project == "SPARKS"
        assert snapshot.active_task == "Phase 3"
        assert snapshot.confidence == 0.95

        loaded_snapshot = service.get_by_id(snapshot.id)

        assert loaded_snapshot is not None
        assert loaded_snapshot.id == snapshot.id


def test_context_snapshot_service_list_by_session():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        session = Session(
            user_id=user.id,
            device_info={"platform": "Windows"},
            session_metadata={},
        )

        db.add(session)
        db.flush()

        service = ContextSnapshotService(db)

        service.create(
            session_id=session.id,
            active_application="Chrome",
            confidence=0.80,
        )

        service.create(
            session_id=session.id,
            active_application="VS Code",
            confidence=0.90,
        )

        snapshots = service.list_by_session(session.id)

        assert len(snapshots) == 2
        assert snapshots[0].active_application == "Chrome"
        assert snapshots[1].active_application == "VS Code"


def test_context_snapshot_service_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        session = Session(
            user_id=user.id,
            device_info={"platform": "Windows"},
            session_metadata={},
        )

        db.add(session)
        db.flush()

        service = ContextSnapshotService(db)

        snapshot = service.create(
            session_id=session.id,
            confidence=0.75,
        )

        snapshot_id = snapshot.id

        service.delete(snapshot)

        assert service.get_by_id(snapshot_id) is None
