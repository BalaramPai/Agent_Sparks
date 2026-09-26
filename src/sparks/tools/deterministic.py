from __future__ import annotations

from sparks.tools.registry import ToolRegistry
from sparks.tools.types import ToolContext, ToolResult


class DeterministicActionExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(
        self,
        text: str,
        context: ToolContext | None = None,
    ) -> ToolResult | None:
        normalized = text.strip()

        if not normalized:
            return None

        matches = [
            tool
            for tool in self.registry.tools()
            if tool.can_handle(normalized)
        ]

        if not matches:
            return None

        if len(matches) > 1:
            return ToolResult(
                success=False,
                tool_name="deterministic_resolver",
                message="Multiple tools matched the request.",
                error="ambiguous_tool_match",
                data={
                    "matches": [tool.name for tool in matches],
                },
            )

        tool = matches[0]

        return self.registry.execute(
            tool.name,
            arguments={"text": normalized},
            context=context,
        )
