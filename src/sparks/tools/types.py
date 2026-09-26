from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolContext:
    source: str = "unknown"
    user_id: int | None = None
    session_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    success: bool
    tool_name: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
