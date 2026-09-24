from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.agent_message import AgentMessage


class AgentMessageRepository:
    """Persistence operations for AgentMessage records."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_id: int,
        sender: str,
        receiver: str,
        objective: str,
        context: str | None = None,
        requested_action: str | None = None,
        expected_result: str | None = None,
    ) -> AgentMessage:
        agent_message = AgentMessage(
            task_id=task_id,
            sender=sender,
            receiver=receiver,
            objective=objective,
            context=context,
            requested_action=requested_action,
            expected_result=expected_result,
        )

        self.db.add(agent_message)
        self.db.commit()
        self.db.refresh(agent_message)

        return agent_message

    def get_by_id(self, agent_message_id: int) -> AgentMessage | None:
        return self.db.get(AgentMessage, agent_message_id)

    def list_by_task(self, task_id: int) -> list[AgentMessage]:
        statement = (
            select(AgentMessage)
            .where(AgentMessage.task_id == task_id)
            .order_by(AgentMessage.timestamp.asc(), AgentMessage.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def delete(self, agent_message: AgentMessage) -> None:
        self.db.delete(agent_message)
        self.db.commit()
