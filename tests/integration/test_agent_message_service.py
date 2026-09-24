from sparks.persistence.database import SessionLocal
from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.models.user import User
from sparks.persistence.repositories.agent_message import AgentMessageRepository
from sparks.persistence.services.agent_message import AgentMessageService


def create_test_task(db):
    user = User(
        preferences={},
        settings={},
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    task = Task(
        user_id=user.id,
        goal="Test AgentMessage service",
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return user, task


def test_send_message():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentMessageService(AgentMessageRepository(db))

        message = service.send_message(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute the next step.",
            context="Planning is complete.",
            requested_action="Execute the operation.",
            expected_result="Successful execution.",
        )

        assert message.id is not None
        assert message.task_id == task.id
        assert message.sender == "planner"
        assert message.receiver == "executor"
        assert message.objective == "Execute the next step."
        assert message.context == "Planning is complete."
        assert message.requested_action == "Execute the operation."
        assert message.expected_result == "Successful execution."


def test_send_message_with_optional_fields():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentMessageService(AgentMessageRepository(db))

        message = service.send_message(
            task_id=task.id,
            sender="executor",
            receiver="planner",
            objective="Report status.",
        )

        assert message.id is not None
        assert message.context is None
        assert message.requested_action is None
        assert message.expected_result is None


def test_get_message():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentMessageService(AgentMessageRepository(db))

        created = service.send_message(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute task.",
        )

        fetched = service.get_message(created.id)

        assert fetched is not None
        assert fetched.id == created.id


def test_list_task_messages():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentMessageService(AgentMessageRepository(db))

        service.send_message(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="First objective.",
        )

        service.send_message(
            task_id=task.id,
            sender="executor",
            receiver="planner",
            objective="Second objective.",
        )

        messages = service.list_task_messages(task.id)

        assert len(messages) == 2


def test_delete_message():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentMessageService(AgentMessageRepository(db))

        message = service.send_message(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute task.",
        )

        message_id = message.id

        service.delete_message(message)

        assert service.get_message(message_id) is None


def test_task_deletion_cascades_to_messages():
    with SessionLocal() as db:
        user, task = create_test_task(db)

        service = AgentMessageService(AgentMessageRepository(db))

        message = service.send_message(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute task.",
        )

        message_id = message.id

        db.delete(task)
        db.commit()

        assert service.get_message(message_id) is None

        db.delete(user)
        db.commit()
