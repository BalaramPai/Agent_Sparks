from sqlalchemy.orm import Session

from sparks.persistence.models import Session as SessionModel
from sparks.persistence.repositories import SessionRepository


class SessionService:
    def __init__(self, db: Session):
        self.db = db
        self.sessions = SessionRepository(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def create_session(
        self,
        user_id: int,
        device_info: dict | None = None,
        session_metadata: dict | None = None,
    ) -> SessionModel:
        return self.sessions.create(
            user_id=user_id,
            device_info=device_info,
            session_metadata=session_metadata,
        )

    def get_session(self, session_id: int) -> SessionModel | None:
        return self.sessions.get_by_id(session_id)

    def end_session(self, session: SessionModel) -> SessionModel:
        return self.sessions.end_session(session)

    def delete_session(self, session: SessionModel) -> None:
        self.sessions.delete(session)