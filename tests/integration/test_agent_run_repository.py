from sparks.persistence.database import SessionLocal
from sparks.persistence.models.agent_run import AgentRunStatus
from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.models.user import User
from sparks.persistence.repositories.agent_run import AgentRunRepository


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
        goal="Test AgentRun persistence",
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return user, task


def test_create_agent_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentRunRepository(db)

        agent_run = repository.create(
            task_id=task.id,
            agent_type="test_agent",
            model="test-model",
        )

        assert agent_run.id is not None
        assert agent_run.task_id == task.id
        assert agent_run.agent_type == "test_agent"
        assert agent_run.model == "test-model"
        assert agent_run.status == AgentRunStatus.RUNNING


def test_get_agent_run_by_id():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentRunRepository(db)

        created = repository.create(
            task_id=task.id,
            agent_type="planner",
            model="llama3.1:8b",
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.task_id == task.id


def test_list_agent_runs_by_task():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentRunRepository(db)

        first = repository.create(
            task_id=task.id,
            agent_type="planner",
            model="llama3.1:8b",
        )

        second = repository.create(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        runs = repository.list_by_task(task.id)

        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids
        assert len(runs) == 2


def test_update_agent_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentRunRepository(db)

        agent_run = repository.create(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        agent_run.status = AgentRunStatus.COMPLETED
        agent_run.tokens = 128
        agent_run.latency = 1.75
        agent_run.result = "Execution completed."

        updated = repository.update(agent_run)

        assert updated.status == AgentRunStatus.COMPLETED
        assert updated.tokens == 128
        assert updated.latency == 1.75
        assert updated.result == "Execution completed."


def test_delete_agent_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = AgentRunRepository(db)

        agent_run = repository.create(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        agent_run_id = agent_run.id

        repository.delete(agent_run)

        assert repository.get_by_id(agent_run_id) is None


def test_task_deletion_cascades_to_agent_runs():
    with SessionLocal() as db:
        user, task = create_test_task(db)

        repository = AgentRunRepository(db)

        agent_run = repository.create(
            task_id=task.id,
            agent_type="executor",
            model="llama3.1:8b",
        )

        agent_run_id = agent_run.id

        db.delete(task)
        db.commit()

        assert repository.get_by_id(agent_run_id) is None

        db.delete(user)
        db.commit()
