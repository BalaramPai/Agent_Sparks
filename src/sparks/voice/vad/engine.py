from dataclasses import dataclass
from enum import Enum


class VadEventType(str, Enum):
    SPEECH_STARTED = "speech_started"
    SPEECH_STOPPED = "speech_stopped"


@dataclass(frozen=True)
class VadConfig:
    """
    Temporal smoothing configuration for VAD.

    Consecutive frames are required before changing the
    externally visible speech state. This prevents a single
    noisy frame from starting or stopping a conversation.
    """

    speech_start_frames: int = 2
    speech_stop_frames: int = 5

    def __post_init__(self) -> None:
        if self.speech_start_frames <= 0:
            raise ValueError("speech_start_frames must be positive")

        if self.speech_stop_frames <= 0:
            raise ValueError("speech_stop_frames must be positive")


@dataclass(frozen=True)
class VadEvent:
    event_type: VadEventType


class VadEngine:
    """
    Stateful VAD coordinator.

    The provider determines whether an individual frame contains
    speech. This class determines when SPARKS should consider a
    conversation to have started or stopped.
    """

    def __init__(
        self,
        detector,
        config: VadConfig | None = None,
    ) -> None:
        self.detector = detector
        self.config = config or VadConfig()

        self._speaking = False
        self._speech_frames = 0
        self._silence_frames = 0

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def process(self, frame) -> VadEvent | None:
        speech = self.detector.is_speech(frame)

        if speech:
            self._speech_frames += 1
            self._silence_frames = 0

            if (
                not self._speaking
                and self._speech_frames >= self.config.speech_start_frames
            ):
                self._speaking = True
                self._speech_frames = 0

                return VadEvent(VadEventType.SPEECH_STARTED)

            return None

        self._speech_frames = 0

        if not self._speaking:
            return None

        self._silence_frames += 1

        if self._silence_frames >= self.config.speech_stop_frames:
            self._speaking = False
            self._silence_frames = 0

            return VadEvent(VadEventType.SPEECH_STOPPED)

        return None

    def reset(self) -> None:
        self._speaking = False
        self._speech_frames = 0
        self._silence_frames = 0
