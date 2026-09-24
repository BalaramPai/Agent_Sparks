from sparks.persistence.database import SessionLocal
from sparks.persistence.models import TaskStatus, User
from sparks.persistence.repositories import TaskRepository


def test_task_repository_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = TaskRepository(db)

        task = repository.create(
            user_id=user.id,
            goal="Build the SPARKS persistence layer.",
            priority=5,
        )

        db.commit()

        assert task.id is not None
        assert task.user_id == user.id
        assert task.goal == "Build the SPARKS persistence layer."
        assert task.priority == 5
        assert task.status == TaskStatus.PENDING
        assert task.parent_task_id is None

        loaded_task = repository.get_by_id(task.id)

        assert loaded_task is not None
        assert loaded_task.id == task.id
        assert loaded_task.goal == task.goal


def test_task_repository_parent_child_relationship():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = TaskRepository(db)

        parent = repository.create(
            user_id=user.id,
            goal="Complete Phase 3.",
            priority=10,
        )

        db.flush()

        child = repository.create(
            user_id=user.id,
            goal="Implement Task persistence.",
            priority=5,
            parent_task_id=parent.id,
        )

        db.commit()

        assert child.parent_task_id == parent.id

        loaded_child = repository.get_by_id(child.id)

        assert loaded_child is not None
        assert loaded_child.parent_task_id == parent.id


def test_task_repository_list_by_user():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = TaskRepository(db)

        repository.create(
            user_id=user.id,
            goal="Task one",
            priority=1,
        )

        repository.create(
            user_id=user.id,
            goal="Task two",
            priority=2,
        )

        db.commit()

        tasks = repository.list_by_user(user.id)

        assert len(tasks) == 2
        assert tasks[0].goal == "Task one"
        assert tasks[1].goal == "Task two"


def test_task_repository_list_by_status():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = TaskRepository(db)

        pending_task = repository.create(
            user_id=user.id,
            goal="Pending task",
            status=TaskStatus.PENDING,
        )

        queued_task = repository.create(
            user_id=user.id,
            goal="Queued task",
            status=TaskStatus.QUEUED,
        )

        db.commit()

        pending_tasks = repository.list_by_status(TaskStatus.PENDING)
        queued_tasks = repository.list_by_status(TaskStatus.QUEUED)

        assert any(task.id == pending_task.id for task in pending_tasks)
        assert any(task.id == queued_task.id for task in queued_tasks)


def test_task_repository_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = TaskRepository(db)

        task = repository.create(
            user_id=user.id,
            goal="Temporary task",
        )

        db.commit()

        task_id = task.id

        repository.delete(task)
        db.commit()

        assert repository.get_by_id(task_id) is None
