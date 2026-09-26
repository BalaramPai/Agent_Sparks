from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sparks.tools.types import ToolContext, ToolResult


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(
        self,
        arguments: dict[str, Any],
        context: ToolContext,
    ) -> ToolResult:
        raise NotImplementedError
