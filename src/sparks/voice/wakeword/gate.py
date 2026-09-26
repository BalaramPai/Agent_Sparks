from __future__ import annotations

from collections.abc import Callable

from sparks.voice.wakeword.base import WakeWordDetector
from sparks.voice.wakeword.policy import (
    ActivationEvent,
    ActivationPolicy,
)
from sparks.voice.wakeword.types import WakeWordDetection


class VoiceActivationGate:
    """
    Combines wake-word detection with activation policy.

    The gate is responsible only for deciding whether incoming audio
    changes the voice activation state.
    """

    def __init__(
        self,
        detector: WakeWordDetector,
        policy: ActivationPolicy,
        *,
        event_callback: Callable[[ActivationEvent], None] | None = None,
    ) -> None:
        self.detector = detector
        self.policy = policy
        self.event_callback = event_callback

    @property
    def is_active(self) -> bool:
        return self.policy.is_active

    def process(self, audio: bytes) -> ActivationEvent | None:
        detection = self.detector.detect(audio)

        event = self.policy.process(detection)

        if event is not None and self.event_callback is not None:
            self.event_callback(event)

        return event

    def deactivate(self) -> ActivationEvent | None:
        event = self.policy.deactivate()

        if event is not None and self.event_callback is not None:
            self.event_callback(event)

        return event

    def reset(self) -> None:
        self.detector.reset()
        self.policy.reset()
