from __future__ import annotations

from sparks.tools.runtime import SparksCommandRuntime
from sparks.tools.types import ToolResult


class VoiceCommandExecutor:
    """
    Bridges finalized voice transcription into the existing
    SPARKS command runtime.

    Voice remains responsible for perception.
    The command runtime remains responsible for routing and execution.
    """

    def __init__(
        self,
        runtime: SparksCommandRuntime | None = None,
    ) -> None:
        self.runtime = runtime or SparksCommandRuntime()

    def execute(self, transcript: str) -> ToolResult | None:
        text = transcript.strip()

        if not text:
            return None

        return self.runtime.execute(text)
