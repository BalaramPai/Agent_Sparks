from abc import ABC, abstractmethod

from sparks.voice.wakeword.types import WakeWordDetection


class WakeWordDetector(ABC):
    """Provider-independent wake-word detection contract."""

    @abstractmethod
    def detect(self, audio: bytes) -> WakeWordDetection:
        """Process an audio frame and return a wake-word detection result."""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset detector state."""
        raise NotImplementedError
