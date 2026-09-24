from sqlalchemy.orm import Session

from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.repositories.task import TaskRepository


class TaskService:
    def __init__(self, db: Session):
        self.repository = TaskRepository(db)
        self.db = db

    def create(
        self,
        user_id: int,
        goal: str,
        priority: int = 0,
        status: TaskStatus = TaskStatus.PENDING,
        parent_task_id: int | None = None,
    ) -> Task:
        try:
            task = self.repository.create(
                user_id=user_id,
                goal=goal,
                priority=priority,
                status=status,
                parent_task_id=parent_task_id,
            )
            self.db.commit()
            return task
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, task_id: int) -> Task | None:
        return self.repository.get_by_id(task_id)

    def list_by_user(self, user_id: int) -> list[Task]:
        return self.repository.list_by_user(user_id)

    def list_by_status(self, status: TaskStatus) -> list[Task]:
        return self.repository.list_by_status(status)

    def delete(self, task: Task) -> None:
        try:
            self.repository.delete(task)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
