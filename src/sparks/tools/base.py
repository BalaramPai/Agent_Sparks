from __future__ import annotations

from abc import ABC, abstractmethod

from sparks.tools.descriptor import ToolDescriptor
from sparks.tools.types import ToolContext, ToolResult


class Tool(ABC):
    name: str
    description: str

    @property
    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            name=self.name,
            description=self.description,
        )

    @abstractmethod
    def can_handle(self, text: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        arguments: dict,
        context: ToolContext,
    ) -> ToolResult:
        raise NotImplementedError
