from sparks.persistence.models.model_run import ModelRun
from sparks.persistence.repositories.model_run import ModelRunRepository


class ModelRunService:
    def __init__(self, repository: ModelRunRepository):
        self.repository = repository

    def record_run(
        self,
        model: str,
        provider: str,
        request_type: str,
        success: bool,
        task_id: int | None = None,
        token_count: int | None = None,
        ttft_ms: float | None = None,
        total_latency_ms: float | None = None,
        tokens_per_second: float | None = None,
        vram_mb: float | None = None,
        cpu_percent: float | None = None,
        ram_mb: float | None = None,
        task_type: str | None = None,
    ) -> ModelRun:
        return self.repository.create(
            model=model,
            provider=provider,
            request_type=request_type,
            success=success,
            task_id=task_id,
            token_count=token_count,
            ttft_ms=ttft_ms,
            total_latency_ms=total_latency_ms,
            tokens_per_second=tokens_per_second,
            vram_mb=vram_mb,
            cpu_percent=cpu_percent,
            ram_mb=ram_mb,
            task_type=task_type,
        )

    def get_run(self, model_run_id: int) -> ModelRun | None:
        return self.repository.get_by_id(model_run_id)

    def list_by_task(self, task_id: int) -> list[ModelRun]:
        return self.repository.list_by_task(task_id)

    def list_by_model(self, model: str) -> list[ModelRun]:
        return self.repository.list_by_model(model)

    def update_run(self, model_run: ModelRun) -> ModelRun:
        return self.repository.update(model_run)

    def delete_run(self, model_run: ModelRun) -> None:
        self.repository.delete(model_run)
