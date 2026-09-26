from dataclasses import dataclass
from enum import Enum


class WakeWordState(str, Enum):
    DISABLED = "disabled"
    LISTENING = "listening"
    DETECTED = "detected"


@dataclass(frozen=True)
class WakeWordDetection:
    detected: bool
    keyword: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Wake-word confidence must be between 0 and 1")

        if self.detected and not self.keyword:
            raise ValueError(
                "A detected wake word must include a keyword"
            )
