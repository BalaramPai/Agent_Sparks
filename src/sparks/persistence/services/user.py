from sqlalchemy.orm import Session

from sparks.persistence.models import User
from sparks.persistence.repositories import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def create_user(
        self,
        preferences: dict | None = None,
        settings: dict | None = None,
    ) -> User:
        return self.users.create(
            preferences=preferences,
            settings=settings,
        )

    def get_user(self, user_id: int) -> User | None:
        return self.users.get_by_id(user_id)

    def delete_user(self, user: User) -> None:
        self.users.delete(user)