from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceActivityFrame:
    """
    A single audio frame presented to a VAD provider.

    Raw PCM remains transient and is never persisted by the
    VAD layer.
    """

    audio: bytes
    sample_rate: int = 16_000
    duration_ms: int = 20

    def __post_init__(self) -> None:
        if not self.audio:
            raise ValueError("audio frame must not be empty")

        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        if self.duration_ms not in (10, 20, 30):
            raise ValueError("duration_ms must be 10, 20, or 30")


class VoiceActivityDetector(ABC):
    """
    Provider-independent VAD interface.

    A concrete implementation decides whether one audio frame
    contains speech. The engine above this interface handles
    temporal state and debouncing.
    """

    @abstractmethod
    def is_speech(self, frame: VoiceActivityFrame) -> bool:
        """Return True when the frame contains speech."""
        raise NotImplementedError
