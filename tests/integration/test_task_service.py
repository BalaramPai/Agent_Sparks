from sparks.persistence.database import SessionLocal
from sparks.persistence.models import TaskStatus, User
from sparks.persistence.services import TaskService


def test_task_service_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = TaskService(db)

        task = service.create(
            user_id=user.id,
            goal="Build durable task persistence.",
            priority=7,
        )

        assert task.id is not None
        assert task.user_id == user.id
        assert task.goal == "Build durable task persistence."
        assert task.priority == 7
        assert task.status == TaskStatus.PENDING

        loaded_task = service.get_by_id(task.id)

        assert loaded_task is not None
        assert loaded_task.id == task.id


def test_task_service_list_by_user():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = TaskService(db)

        service.create(
            user_id=user.id,
            goal="Task one",
            priority=1,
        )

        service.create(
            user_id=user.id,
            goal="Task two",
            priority=2,
        )

        tasks = service.list_by_user(user.id)

        assert len(tasks) == 2
        assert tasks[0].goal == "Task one"
        assert tasks[1].goal == "Task two"


def test_task_service_list_by_status():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = TaskService(db)

        pending_task = service.create(
            user_id=user.id,
            goal="Pending task",
            status=TaskStatus.PENDING,
        )

        queued_task = service.create(
            user_id=user.id,
            goal="Queued task",
            status=TaskStatus.QUEUED,
        )

        pending_tasks = service.list_by_status(TaskStatus.PENDING)
        queued_tasks = service.list_by_status(TaskStatus.QUEUED)

        assert any(task.id == pending_task.id for task in pending_tasks)
        assert any(task.id == queued_task.id for task in queued_tasks)


def test_task_service_parent_task():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = TaskService(db)

        parent = service.create(
            user_id=user.id,
            goal="Complete Phase 3.",
        )

        child = service.create(
            user_id=user.id,
            goal="Complete Task persistence.",
            parent_task_id=parent.id,
        )

        assert child.parent_task_id == parent.id

        loaded_child = service.get_by_id(child.id)

        assert loaded_child is not None
        assert loaded_child.parent_task_id == parent.id


def test_task_service_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = TaskService(db)

        task = service.create(
            user_id=user.id,
            goal="Temporary task",
        )

        task_id = task.id

        service.delete(task)

        assert service.get_by_id(task_id) is None
