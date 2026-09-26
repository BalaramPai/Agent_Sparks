from __future__ import annotations

from sparks.router.router import IntentRouter
from sparks.router.intent.types import IntentRoute

from sparks.tools.application.chrome import OpenChromeTool
from sparks.tools.application.url import OpenUrlTool
from sparks.tools.registry import ToolRegistry
from sparks.tools.selector import ToolSelector
from sparks.tools.types import ToolContext, ToolResult


class SparksCommandRuntime:
    def __init__(self) -> None:
        self.router = IntentRouter()

        self.registry = ToolRegistry()
        self.registry.register(OpenChromeTool())
        self.registry.register(OpenUrlTool())

        self.selector = ToolSelector(self.registry)

    def execute(self, text: str) -> ToolResult | None:
        normalized = text.strip()

        if not normalized:
            return None

        intent = self.router.route(normalized)

        if intent.route != IntentRoute.DETERMINISTIC:
            return None

        selection = self.selector.select(normalized)

        if selection.tool is None:
            return None

        return self.registry.execute(
            selection.tool.name,
            arguments={
                "text": normalized,
            },
            context=ToolContext(
                source="command",
            ),
        )
