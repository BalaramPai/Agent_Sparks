from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        preferences: dict | None = None,
        settings: dict | None = None,
    ) -> User:
        user = User(
            preferences=preferences or {},
            settings=settings or {},
        )

        self.db.add(user)
        self.db.flush()

        return user

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.db.scalar(statement)

    def delete(self, user: User) -> None:
        self.db.delete(user)