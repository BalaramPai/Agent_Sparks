from dataclasses import dataclass
from enum import Enum


class TranscriptionType(str, Enum):
    PARTIAL = "partial"
    FINAL = "final"


@dataclass(frozen=True)
class TranscriptionResult:
    """
    A transcription update produced by an STT provider.

    Partial results may change as more audio becomes available.
    Final results represent the completed utterance.
    """

    text: str
    result_type: TranscriptionType
    confidence: float | None = None
    language: str | None = None

    @property
    def is_partial(self) -> bool:
        return self.result_type == TranscriptionType.PARTIAL

    @property
    def is_final(self) -> bool:
        return self.result_type == TranscriptionType.FINAL

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("transcription text must be a string")

        if not self.text.strip():
            raise ValueError("transcription text must not be empty")

        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
