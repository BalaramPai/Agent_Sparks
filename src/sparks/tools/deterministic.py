from __future__ import annotations

import re

from sparks.tools.types import ToolContext, ToolResult
from sparks.tools.registry import ToolRegistry


class DeterministicActionExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(
        self,
        text: str,
        context: ToolContext | None = None,
    ) -> ToolResult | None:
        normalized = text.strip().lower()

        if re.search(
            r"\b(open|launch|start)\b.*\b(chrome|google chrome)\b",
            normalized,
        ):
            return self.registry.execute(
                "open_chrome",
                context=context,
            )

        return None
