from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sparks.voice.wakeword.types import WakeWordDetection


class ActivationState(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"


@dataclass(frozen=True)
class ActivationConfig:
    enabled: bool = True
    activation_timeout_frames: int = 250

    def __post_init__(self) -> None:
        if self.activation_timeout_frames <= 0:
            raise ValueError(
                "activation_timeout_frames must be positive"
            )


@dataclass(frozen=True)
class ActivationEvent:
    state: ActivationState
    keyword: str | None = None
    confidence: float | None = None


class ActivationPolicy:
    """
    Controls whether SPARKS is currently accepting voice input
    after wake-word activation.

    The policy is intentionally independent of any wake-word provider.
    """

    def __init__(
        self,
        config: ActivationConfig | None = None,
    ) -> None:
        self.config = config or ActivationConfig()
        self._state = (
            ActivationState.INACTIVE
            if self.config.enabled
            else ActivationState.ACTIVE
        )
        self._remaining_frames = 0

    @property
    def state(self) -> ActivationState:
        return self._state

    @property
    def is_active(self) -> bool:
        return self._state == ActivationState.ACTIVE

    def process(
        self,
        detection: WakeWordDetection,
    ) -> ActivationEvent | None:
        if not self.config.enabled:
            return None

        if detection.detected:
            self._state = ActivationState.ACTIVE
            self._remaining_frames = self.config.activation_timeout_frames

            return ActivationEvent(
                state=ActivationState.ACTIVE,
                keyword=detection.keyword,
                confidence=detection.confidence,
            )

        if self._state != ActivationState.ACTIVE:
            return None

        self._remaining_frames -= 1

        if self._remaining_frames <= 0:
            self._state = ActivationState.INACTIVE

            return ActivationEvent(
                state=ActivationState.INACTIVE,
            )

        return None

    def deactivate(self) -> ActivationEvent | None:
        if self._state != ActivationState.ACTIVE:
            return None

        self._state = ActivationState.INACTIVE
        self._remaining_frames = 0

        return ActivationEvent(
            state=ActivationState.INACTIVE,
        )

    def reset(self) -> None:
        self._state = (
            ActivationState.INACTIVE
            if self.config.enabled
            else ActivationState.ACTIVE
        )
        self._remaining_frames = 0
