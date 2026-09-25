from sparks.persistence.database import SessionLocal
from sparks.persistence.models.model_run import ModelRun
from sparks.persistence.repositories.model_run import ModelRunRepository


def test_create_model_run():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        model_run = repository.create(
            model="llama3.1:8b",
            provider="ollama",
            request_type="general",
            success=True,
            token_count=128,
            ttft_ms=120.5,
            total_latency_ms=1500.0,
            tokens_per_second=85.3,
            vram_mb=3200.0,
            cpu_percent=42.5,
            ram_mb=7800.0,
            task_type="general",
        )

        assert model_run.id is not None
        assert model_run.model == "llama3.1:8b"
        assert model_run.provider == "ollama"
        assert model_run.request_type == "general"
        assert model_run.success is True
        assert model_run.token_count == 128
        assert model_run.ttft_ms == 120.5


def test_create_model_run_minimal():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        model_run = repository.create(
            model="test-model",
            provider="test-provider",
            request_type="test",
            success=False,
        )

        assert model_run.id is not None
        assert model_run.model == "test-model"
        assert model_run.success is False
        assert model_run.token_count is None


def test_get_model_run():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        created = repository.create(
            model="test-model",
            provider="ollama",
            request_type="general",
            success=True,
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.model == "test-model"


def test_list_by_task():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        from sparks.persistence.models.task import Task
        from sparks.persistence.models.user import User

        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

        task = Task(
            user_id=user.id,
            goal="Test model task",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        first = repository.create(
            model="model-a",
            provider="ollama",
            request_type="general",
            success=True,
            task_id=task.id,
        )

        second = repository.create(
            model="model-b",
            provider="ollama",
            request_type="reasoning",
            success=True,
            task_id=task.id,
        )

        runs = repository.list_by_task(task.id)
        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids


def test_list_by_model():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        first = repository.create(
            model="llama3.1:8b",
            provider="ollama",
            request_type="general",
            success=True,
        )

        second = repository.create(
            model="llama3.1:8b",
            provider="ollama",
            request_type="reasoning",
            success=True,
        )

        repository.create(
            model="other-model",
            provider="ollama",
            request_type="general",
            success=True,
        )

        runs = repository.list_by_model("llama3.1:8b")
        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids


def test_update_model_run():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        model_run = repository.create(
            model="test-model",
            provider="ollama",
            request_type="general",
            success=False,
        )

        model_run.success = True
        model_run.total_latency_ms = 1000.0

        updated = repository.update(model_run)

        assert updated.success is True
        assert updated.total_latency_ms == 1000.0


def test_delete_model_run():
    with SessionLocal() as db:
        repository = ModelRunRepository(db)

        model_run = repository.create(
            model="test-model",
            provider="ollama",
            request_type="general",
            success=True,
        )

        model_run_id = model_run.id

        repository.delete(model_run)

        assert repository.get_by_id(model_run_id) is None
