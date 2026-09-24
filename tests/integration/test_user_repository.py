from sparks.persistence.database import SessionLocal
from sparks.persistence.repositories import UserRepository


def test_user_repository_create_and_get():
    with SessionLocal() as db:
        repository = UserRepository(db)

        user = repository.create(
            preferences={"theme": "dark"},
            settings={"notifications": True},
        )

        db.commit()

        loaded_user = repository.get_by_id(user.id)

        assert loaded_user is not None
        assert loaded_user.id == user.id
        assert loaded_user.preferences == {"theme": "dark"}
        assert loaded_user.settings == {"notifications": True}