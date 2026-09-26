from __future__ import annotations

from dataclasses import dataclass

from sparks.tools.base import Tool
from sparks.tools.registry import ToolRegistry


@dataclass(frozen=True)
class ToolSelection:
    tool: Tool | None
    confidence: float
    reason: str


class ToolSelector:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def select(self, text: str) -> ToolSelection:
        normalized = text.strip()

        if not normalized:
            return ToolSelection(
                tool=None,
                confidence=0.0,
                reason="empty_request",
            )

        matches = [
            tool
            for tool in self.registry.tools()
            if tool.can_handle(normalized)
        ]

        if len(matches) == 1:
            return ToolSelection(
                tool=matches[0],
                confidence=1.0,
                reason="deterministic_match",
            )

        if len(matches) > 1:
            return ToolSelection(
                tool=None,
                confidence=0.0,
                reason="ambiguous_match",
            )

        return ToolSelection(
            tool=None,
            confidence=0.0,
            reason="no_matching_tool",
        )
