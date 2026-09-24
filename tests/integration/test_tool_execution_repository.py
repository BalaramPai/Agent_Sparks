from sparks.persistence.database import SessionLocal
from sparks.persistence.models.agent_run import AgentRunStatus
from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.models.user import User
from sparks.persistence.repositories.agent_run import AgentRunRepository
from sparks.persistence.repositories.tool_execution import ToolExecutionRepository


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
        goal="Test ToolExecution persistence",
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return user, task


def create_test_agent_run(db, task_id):
    repository = AgentRunRepository(db)

    return repository.create(
        task_id=task_id,
        agent_type="executor",
        model="test-model",
        status=AgentRunStatus.RUNNING,
    )


def test_create_tool_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)
        agent_run = create_test_agent_run(db, task.id)

        repository = ToolExecutionRepository(db)

        execution = repository.create(
            task_id=task.id,
            agent_run_id=agent_run.id,
            tool_name="test_tool",
            status="COMPLETED",
            arguments='{"input": "test"}',
            result='{"output": "success"}',
            latency_ms=125.5,
            risk_level="LOW",
            verification_result="VERIFIED",
        )

        assert execution.id is not None
        assert execution.task_id == task.id
        assert execution.agent_run_id == agent_run.id
        assert execution.tool_name == "test_tool"
        assert execution.status == "COMPLETED"
        assert execution.arguments == '{"input": "test"}'
        assert execution.result == '{"output": "success"}'
        assert execution.latency_ms == 125.5
        assert execution.risk_level == "LOW"
        assert execution.verification_result == "VERIFIED"
        assert execution.timestamp is not None


def test_create_tool_execution_without_agent_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = ToolExecutionRepository(db)

        execution = repository.create(
            task_id=task.id,
            tool_name="standalone_tool",
            status="RUNNING",
        )

        assert execution.id is not None
        assert execution.agent_run_id is None
        assert execution.arguments is None
        assert execution.result is None
        assert execution.latency_ms is None
        assert execution.risk_level is None
        assert execution.verification_result is None


def test_get_tool_execution_by_id():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = ToolExecutionRepository(db)

        created = repository.create(
            task_id=task.id,
            tool_name="test_tool",
            status="RUNNING",
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.task_id == task.id


def test_list_tool_executions_by_task():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = ToolExecutionRepository(db)

        first = repository.create(
            task_id=task.id,
            tool_name="first_tool",
            status="COMPLETED",
        )

        second = repository.create(
            task_id=task.id,
            tool_name="second_tool",
            status="FAILED",
        )

        executions = repository.list_by_task(task.id)

        execution_ids = [execution.id for execution in executions]

        assert first.id in execution_ids
        assert second.id in execution_ids
        assert len(executions) == 2


def test_list_tool_executions_by_agent_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)
        agent_run = create_test_agent_run(db, task.id)

        repository = ToolExecutionRepository(db)

        first = repository.create(
            task_id=task.id,
            agent_run_id=agent_run.id,
            tool_name="first_tool",
            status="COMPLETED",
        )

        second = repository.create(
            task_id=task.id,
            agent_run_id=agent_run.id,
            tool_name="second_tool",
            status="COMPLETED",
        )

        executions = repository.list_by_agent_run(agent_run.id)

        execution_ids = [execution.id for execution in executions]

        assert first.id in execution_ids
        assert second.id in execution_ids
        assert len(executions) == 2


def test_update_tool_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = ToolExecutionRepository(db)

        execution = repository.create(
            task_id=task.id,
            tool_name="test_tool",
            status="RUNNING",
        )

        execution.status = "COMPLETED"
        execution.result = "Execution successful."
        execution.latency_ms = 250.0
        execution.verification_result = "VERIFIED"

        updated = repository.update(execution)

        assert updated.status == "COMPLETED"
        assert updated.result == "Execution successful."
        assert updated.latency_ms == 250.0
        assert updated.verification_result == "VERIFIED"


def test_agent_run_deletion_sets_agent_run_id_to_null():
    with SessionLocal() as db:
        _, task = create_test_task(db)
        agent_run = create_test_agent_run(db, task.id)

        repository = ToolExecutionRepository(db)

        execution = repository.create(
            task_id=task.id,
            agent_run_id=agent_run.id,
            tool_name="test_tool",
            status="COMPLETED",
        )

        execution_id = execution.id

        db.delete(agent_run)
        db.commit()

        updated = repository.get_by_id(execution_id)

        assert updated is not None
        assert updated.agent_run_id is None


def test_delete_tool_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        repository = ToolExecutionRepository(db)

        execution = repository.create(
            task_id=task.id,
            tool_name="test_tool",
            status="COMPLETED",
        )

        execution_id = execution.id

        repository.delete(execution)

        assert repository.get_by_id(execution_id) is None


def test_task_deletion_cascades_to_tool_executions():
    with SessionLocal() as db:
        user, task = create_test_task(db)

        repository = ToolExecutionRepository(db)

        execution = repository.create(
            task_id=task.id,
            tool_name="test_tool",
            status="COMPLETED",
        )

        execution_id = execution.id

        db.delete(task)
        db.commit()

        assert repository.get_by_id(execution_id) is None

        db.delete(user)
        db.commit()
