from sqlalchemy.orm import Session

from sparks.persistence.models.task_step import TaskStep, TaskStepStatus
from sparks.persistence.repositories.task_step import TaskStepRepository


class TaskStepService:
    def __init__(self, db: Session):
        self.repository = TaskStepRepository(db)
        self.db = db

    def create(
        self,
        task_id: int,
        step_order: int,
        description: str,
        status: TaskStepStatus = TaskStepStatus.PENDING,
    ) -> TaskStep:
        try:
            step = self.repository.create(
                task_id=task_id,
                step_order=step_order,
                description=description,
                status=status,
            )
            self.db.commit()
            return step
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, step_id: int) -> TaskStep | None:
        return self.repository.get_by_id(step_id)

    def list_by_task(self, task_id: int) -> list[TaskStep]:
        return self.repository.list_by_task(task_id)

    def list_by_status(self, status: TaskStepStatus) -> list[TaskStep]:
        return self.repository.list_by_status(status)

    def delete(self, step: TaskStep) -> None:
        try:
            self.repository.delete(step)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
