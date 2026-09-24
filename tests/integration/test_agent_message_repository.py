from sparks.persistence.database import SessionLocal
from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.models.user import User
from sparks.persistence.repositories.agent_message import AgentMessageRepository


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
        goal="Test AgentMessage persistence",
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return user, task


def test_create_agent_message():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentMessageRepository(db)

        message = repository.create(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute the next task step.",
            context="The task has been planned.",
            requested_action="Run the assigned operation.",
            expected_result="Operation completes successfully.",
        )

        assert message.id is not None
        assert message.task_id == task.id
        assert message.sender == "planner"
        assert message.receiver == "executor"
        assert message.objective == "Execute the next task step."
        assert message.context == "The task has been planned."
        assert message.requested_action == "Run the assigned operation."
        assert message.expected_result == "Operation completes successfully."
        assert message.timestamp is not None


def test_create_agent_message_with_optional_fields():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentMessageRepository(db)

        message = repository.create(
            task_id=task.id,
            sender="executor",
            receiver="planner",
            objective="Report execution status.",
        )

        assert message.id is not None
        assert message.context is None
        assert message.requested_action is None
        assert message.expected_result is None


def test_get_agent_message_by_id():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentMessageRepository(db)

        created = repository.create(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute task.",
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.task_id == task.id


def test_list_agent_messages_by_task():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentMessageRepository(db)

        first = repository.create(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="First objective.",
        )

        second = repository.create(
            task_id=task.id,
            sender="executor",
            receiver="planner",
            objective="Second objective.",
        )

        messages = repository.list_by_task(task.id)

        message_ids = [message.id for message in messages]

        assert first.id in message_ids
        assert second.id in message_ids
        assert len(messages) == 2


def test_delete_agent_message():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentMessageRepository(db)

        message = repository.create(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute task.",
        )

        message_id = message.id

        repository.delete(message)

        assert repository.get_by_id(message_id) is None


def test_task_deletion_cascades_to_agent_messages():
    with SessionLocal() as db:
        user, task = create_test_task(db)

        repository = AgentMessageRepository(db)

        message = repository.create(
            task_id=task.id,
            sender="planner",
            receiver="executor",
            objective="Execute task.",
        )

        message_id = message.id

        db.delete(task)
        db.commit()

        assert repository.get_by_id(message_id) is None

        db.delete(user)
        db.commit()
