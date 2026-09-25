from sparks.persistence.database import SessionLocal
from sparks.persistence.repositories.performance_metric import (
    PerformanceMetricRepository,
)
from sparks.persistence.services.performance_metric import (
    PerformanceMetricService,
)


def test_record_metric():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        metric = service.record_metric(
            metric_type="model_latency",
            value=1250.0,
            unit="ms",
            component="inference",
            metadata={"model": "llama3.1:8b"},
        )

        assert metric.id is not None
        assert metric.metric_type == "model_latency"
        assert metric.value == 1250.0
        assert metric.metric_metadata == {"model": "llama3.1:8b"}


def test_get_metric():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        created = service.record_metric(
            metric_type="routing_latency",
            value=5.0,
            unit="ms",
            component="router",
        )

        fetched = service.get_metric(created.id)

        assert fetched is not None
        assert fetched.id == created.id


def test_list_by_component():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        first = service.record_metric(
            metric_type="model_latency",
            value=1000.0,
            unit="ms",
            component="inference",
        )

        second = service.record_metric(
            metric_type="tokens_per_second",
            value=80.0,
            unit="tokens/sec",
            component="inference",
        )

        metrics = service.list_by_component("inference")
        metric_ids = [metric.id for metric in metrics]

        assert first.id in metric_ids
        assert second.id in metric_ids


def test_list_by_metric_type():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        first = service.record_metric(
            metric_type="model_latency",
            value=1000.0,
            unit="ms",
            component="inference",
        )

        second = service.record_metric(
            metric_type="model_latency",
            value=1100.0,
            unit="ms",
            component="inference",
        )

        metrics = service.list_by_metric_type("model_latency")
        metric_ids = [metric.id for metric in metrics]

        assert first.id in metric_ids
        assert second.id in metric_ids


def test_list_by_task():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        from sparks.persistence.models.task import Task
        from sparks.persistence.models.user import User

        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

        task = Task(
            user_id=user.id,
            goal="Performance task",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        metric = service.record_metric(
            metric_type="end_to_end_latency",
            value=2000.0,
            unit="ms",
            component="runtime",
            task_id=task.id,
        )

        metrics = service.list_by_task(task.id)

        assert len(metrics) == 1
        assert metrics[0].id == metric.id


def test_update_metric():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        metric = service.record_metric(
            metric_type="tool_latency",
            value=50.0,
            unit="ms",
            component="tool",
        )

        metric.value = 75.0

        updated = service.update_metric(metric)

        assert updated.value == 75.0


def test_delete_metric():
    with SessionLocal() as db:
        service = PerformanceMetricService(
            PerformanceMetricRepository(db)
        )

        metric = service.record_metric(
            metric_type="network_latency",
            value=30.0,
            unit="ms",
            component="network",
        )

        metric_id = metric.id

        service.delete_metric(metric)

        assert service.get_metric(metric_id) is None
