from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models import Session as SessionModel


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        device_info: dict | None = None,
        session_metadata: dict | None = None,
    ) -> SessionModel:
        session = SessionModel(
            user_id=user_id,
            device_info=device_info or {},
            session_metadata=session_metadata or {},
        )

        self.db.add(session)
        self.db.flush()

        return session

    def get_by_id(self, session_id: int) -> SessionModel | None:
        statement = select(SessionModel).where(
            SessionModel.id == session_id
        )

        return self.db.scalar(statement)

    def end_session(self, session: SessionModel) -> SessionModel:
        from datetime import datetime, timezone

        session.ended_at = datetime.now(timezone.utc)

        self.db.flush()

        return session

    def delete(self, session: SessionModel) -> None:
        self.db.delete(session)