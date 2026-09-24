from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Task, TaskStepStatus, User
from sparks.persistence.services import TaskStepService


def test_task_step_service_create_and_get():
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

        service = TaskStepService(db)

        step = service.create(
            task_id=task.id,
            step_order=1,
            description="Implement TaskStep persistence.",
        )

        assert step.id is not None
        assert step.task_id == task.id
        assert step.step_order == 1
        assert step.description == "Implement TaskStep persistence."
        assert step.status == TaskStepStatus.PENDING

        loaded_step = service.get_by_id(step.id)

        assert loaded_step is not None
        assert loaded_step.id == step.id


def test_task_step_service_list_by_task():
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

        service = TaskStepService(db)

        service.create(
            task_id=task.id,
            step_order=1,
            description="First step",
        )

        service.create(
            task_id=task.id,
            step_order=2,
            description="Second step",
        )

        steps = service.list_by_task(task.id)

        assert len(steps) == 2
        assert steps[0].description == "First step"
        assert steps[1].description == "Second step"


def test_task_step_service_list_by_status():
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

        service = TaskStepService(db)

        pending_step = service.create(
            task_id=task.id,
            step_order=1,
            description="Pending step",
            status=TaskStepStatus.PENDING,
        )

        completed_step = service.create(
            task_id=task.id,
            step_order=2,
            description="Completed step",
            status=TaskStepStatus.COMPLETED,
        )

        pending_steps = service.list_by_status(TaskStepStatus.PENDING)
        completed_steps = service.list_by_status(TaskStepStatus.COMPLETED)

        assert any(step.id == pending_step.id for step in pending_steps)
        assert any(step.id == completed_step.id for step in completed_steps)


def test_task_step_service_delete():
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

        service = TaskStepService(db)

        step = service.create(
            task_id=task.id,
            step_order=1,
            description="Temporary step",
        )

        step_id = step.id

        service.delete(step)

        assert service.get_by_id(step_id) is None
