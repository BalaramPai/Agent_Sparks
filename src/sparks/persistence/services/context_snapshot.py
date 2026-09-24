from sqlalchemy.orm import Session

from sparks.persistence.models.context_snapshot import ContextSnapshot
from sparks.persistence.repositories.context_snapshot import ContextSnapshotRepository


class ContextSnapshotService:
    def __init__(self, db: Session):
        self.repository = ContextSnapshotRepository(db)
        self.db = db

    def create(
        self,
        session_id: int,
        confidence: float,
        active_application: str | None = None,
        active_project: str | None = None,
        active_task: str | None = None,
        relevant_context: str | None = None,
        snapshot_metadata: dict | None = None,
    ) -> ContextSnapshot:
        try:
            snapshot = self.repository.create(
                session_id=session_id,
                confidence=confidence,
                active_application=active_application,
                active_project=active_project,
                active_task=active_task,
                relevant_context=relevant_context,
                snapshot_metadata=snapshot_metadata,
            )
            self.db.commit()
            return snapshot
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, snapshot_id: int) -> ContextSnapshot | None:
        return self.repository.get_by_id(snapshot_id)

    def list_by_session(self, session_id: int) -> list[ContextSnapshot]:
        return self.repository.list_by_session(session_id)

    def delete(self, snapshot: ContextSnapshot) -> None:
        try:
            self.repository.delete(snapshot)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
