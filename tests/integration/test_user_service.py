from sparks.persistence.database import SessionLocal
from sparks.persistence.services import UserService


def test_user_service_create_and_get():
    with SessionLocal() as db:
        service = UserService(db)

        user = service.create_user(
            preferences={"theme": "dark"},
            settings={"notifications": True},
        )

        service.commit()

        loaded_user = service.get_user(user.id)

        assert loaded_user is not None
        assert loaded_user.id == user.id
        assert loaded_user.preferences == {"theme": "dark"}
        assert loaded_user.settings == {"notifications": True}