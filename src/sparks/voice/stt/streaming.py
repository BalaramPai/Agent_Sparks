from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StreamingTranscriptionType(str, Enum):
    PARTIAL = "partial"
    FINAL = "final"


@dataclass(frozen=True)
class StreamingTranscriptionResult:
    text: str
    result_type: StreamingTranscriptionType
    confidence: float | None = None
    language: str | None = None
    sequence: int = 0
