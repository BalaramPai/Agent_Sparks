from sparks.persistence.database import SessionLocal
from sparks.persistence.models.agent_run import AgentRunStatus
from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.models.user import User
from sparks.persistence.repositories.agent_run import AgentRunRepository
from sparks.persistence.services.agent_run import AgentRunService


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
        goal="Test AgentRun service",
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return user, task


def test_start_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentRunService(AgentRunRepository(db))

        agent_run = service.start_run(
            task_id=task.id,
            agent_type="planner",
            model="llama3.1:8b",
        )

        assert agent_run.id is not None
        assert agent_run.task_id == task.id
        assert agent_run.agent_type == "planner"
        assert agent_run.model == "llama3.1:8b"
        assert agent_run.status == AgentRunStatus.RUNNING


def test_get_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentRunService(AgentRunRepository(db))

        created = service.start_run(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        fetched = service.get_run(created.id)

        assert fetched is not None
        assert fetched.id == created.id


def test_list_task_runs():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentRunService(AgentRunRepository(db))

        service.start_run(
            task_id=task.id,
            agent_type="planner",
            model="llama3.1:8b",
        )
        service.start_run(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        runs = service.list_task_runs(task.id)

        assert len(runs) == 2


def test_complete_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentRunService(AgentRunRepository(db))

        agent_run = service.start_run(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        completed = service.complete_run(
            agent_run,
            result="Task completed successfully.",
            tokens=256,
            latency=2.4,
        )

        assert completed.status == AgentRunStatus.COMPLETED
        assert completed.result == "Task completed successfully."
        assert completed.tokens == 256
        assert completed.latency == 2.4


def test_fail_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentRunService(AgentRunRepository(db))

        agent_run = service.start_run(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        failed = service.fail_run(
            agent_run,
            error="Execution failed.",
            latency=1.2,
        )

        assert failed.status == AgentRunStatus.FAILED
        assert failed.error == "Execution failed."
        assert failed.latency == 1.2


def test_cancel_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = AgentRunService(AgentRunRepository(db))

        agent_run = service.start_run(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        cancelled = service.cancel_run(agent_run)

        assert cancelled.status == AgentRunStatus.CANCELLED
