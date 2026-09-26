from __future__ import annotations

from sparks.router.router import IntentRouter
from sparks.router.intent.types import IntentRoute

from sparks.tools.application.chrome import OpenChromeTool
from sparks.tools.deterministic import DeterministicActionExecutor
from sparks.tools.registry import ToolRegistry
from sparks.tools.types import ToolContext, ToolResult


class SparksCommandRuntime:
    def __init__(self) -> None:
        self.router = IntentRouter()

        self.registry = ToolRegistry()
        self.registry.register(OpenChromeTool())

        self.deterministic = DeterministicActionExecutor(
            self.registry
        )

    def execute(self, text: str) -> ToolResult | None:
        intent = self.router.route(text)

        if intent.route != IntentRoute.DETERMINISTIC:
            return None

        return self.deterministic.execute(
            text,
            ToolContext(source="command"),
        )
