from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Task, TaskStepStatus, User
from sparks.persistence.repositories import TaskStepRepository


def test_task_step_repository_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        task = Task(
            user_id=user.id,
            goal="Complete Phase 3",
        )

        db.add(task)
        db.flush()

        repository = TaskStepRepository(db)

        step = repository.create(
            task_id=task.id,
            step_order=1,
            description="Implement TaskStep persistence.",
        )

        db.commit()

        assert step.id is not None
        assert step.task_id == task.id
        assert step.step_order == 1
        assert step.description == "Implement TaskStep persistence."
        assert step.status == TaskStepStatus.PENDING

        loaded_step = repository.get_by_id(step.id)

        assert loaded_step is not None
        assert loaded_step.id == step.id
        assert loaded_step.task_id == task.id


def test_task_step_repository_list_by_task():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        task = Task(
            user_id=user.id,
            goal="Complete Phase 3",
        )

        db.add(task)
        db.flush()

        repository = TaskStepRepository(db)

        third = repository.create(
            task_id=task.id,
            step_order=3,
            description="Third step",
        )

        first = repository.create(
            task_id=task.id,
            step_order=1,
            description="First step",
        )

        second = repository.create(
            task_id=task.id,
            step_order=2,
            description="Second step",
        )

        db.commit()

        steps = repository.list_by_task(task.id)

        assert len(steps) == 3
        assert [step.id for step in steps] == [
            first.id,
            second.id,
            third.id,
        ]
        assert [step.step_order for step in steps] == [1, 2, 3]


def test_task_step_repository_list_by_status():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        task = Task(
            user_id=user.id,
            goal="Complete Phase 3",
        )

        db.add(task)
        db.flush()

        repository = TaskStepRepository(db)

        pending_step = repository.create(
            task_id=task.id,
            step_order=1,
            description="Pending step",
            status=TaskStepStatus.PENDING,
        )

        completed_step = repository.create(
            task_id=task.id,
            step_order=2,
            description="Completed step",
            status=TaskStepStatus.COMPLETED,
        )

        db.commit()

        pending_steps = repository.list_by_status(TaskStepStatus.PENDING)
        completed_steps = repository.list_by_status(TaskStepStatus.COMPLETED)

        assert any(step.id == pending_step.id for step in pending_steps)
        assert any(step.id == completed_step.id for step in completed_steps)


def test_task_step_repository_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        task = Task(
            user_id=user.id,
            goal="Complete Phase 3",
        )

        db.add(task)
        db.flush()

        repository = TaskStepRepository(db)

        step = repository.create(
            task_id=task.id,
            step_order=1,
            description="Temporary step",
        )

        db.commit()

        step_id = step.id

        repository.delete(step)
        db.commit()

        assert repository.get_by_id(step_id) is None
