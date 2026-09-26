from __future__ import annotations

from sparks.tools.base import Tool
from sparks.tools.descriptor import ToolDescriptor
from sparks.tools.types import ToolContext, ToolResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = tool.name.strip().lower()

        if not name:
            raise ValueError("Tool name cannot be empty")

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        normalized = name.strip().lower()

        try:
            return self._tools[normalized]
        except KeyError:
            raise KeyError(f"Unknown tool: {name}") from None

    def tools(self) -> list[Tool]:
        return list(self._tools.values())

    def list_tools(self) -> list[str]:
        return sorted(self._tools)

    def descriptors(self) -> list[ToolDescriptor]:
        return [
            tool.descriptor
            for tool in self.tools()
        ]

    def execute(
        self,
        name: str,
        arguments: dict | None = None,
        context: ToolContext | None = None,
    ) -> ToolResult:
        tool = self.get(name)

        return tool.execute(
            arguments or {},
            context or ToolContext(),
        )
