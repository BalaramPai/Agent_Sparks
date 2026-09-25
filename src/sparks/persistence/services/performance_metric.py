from sparks.persistence.models.performance_metric import PerformanceMetric
from sparks.persistence.repositories.performance_metric import (
    PerformanceMetricRepository,
)


class PerformanceMetricService:
    def __init__(self, repository: PerformanceMetricRepository):
        self.repository = repository

    def record_metric(
        self,
        metric_type: str,
        value: float,
        unit: str,
        component: str,
        task_id: int | None = None,
        model_run_id: int | None = None,
        metadata: dict | None = None,
    ) -> PerformanceMetric:
        return self.repository.create(
            metric_type=metric_type,
            value=value,
            unit=unit,
            component=component,
            task_id=task_id,
            model_run_id=model_run_id,
            metadata=metadata,
        )

    def get_metric(self, metric_id: int) -> PerformanceMetric | None:
        return self.repository.get_by_id(metric_id)

    def list_by_component(
        self,
        component: str,
    ) -> list[PerformanceMetric]:
        return self.repository.list_by_component(component)

    def list_by_metric_type(
        self,
        metric_type: str,
    ) -> list[PerformanceMetric]:
        return self.repository.list_by_metric_type(metric_type)

    def list_by_task(
        self,
        task_id: int,
    ) -> list[PerformanceMetric]:
        return self.repository.list_by_task(task_id)

    def update_metric(
        self,
        metric: PerformanceMetric,
    ) -> PerformanceMetric:
        return self.repository.update(metric)

    def delete_metric(self, metric: PerformanceMetric) -> None:
        self.repository.delete(metric)
