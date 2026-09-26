from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InterruptionReason(str, Enum):
    USER_SPEECH = "user_speech"
    USER_REQUEST = "user_request"
    SYSTEM = "system"


@dataclass(frozen=True)
class InterruptionEvent:
    reason: InterruptionReason
    source: str = "unknown"


class InterruptionController:
    """
    Coordinates interruption of an active voice operation.

    The controller intentionally stays provider-independent.
    VoicePipeline owns the actual cancellation operation.
    """

    def __init__(self, cancel_callback) -> None:
        if not callable(cancel_callback):
            raise TypeError("cancel_callback must be callable")

        self._cancel_callback = cancel_callback
        self._interrupted = False
        self._last_event: InterruptionEvent | None = None

    @property
    def interrupted(self) -> bool:
        return self._interrupted

    @property
    def last_event(self) -> InterruptionEvent | None:
        return self._last_event

    def interrupt(
        self,
        reason: InterruptionReason = InterruptionReason.USER_SPEECH,
        *,
        source: str = "unknown",
    ) -> bool:
        event = InterruptionEvent(
            reason=reason,
            source=source,
        )

        cancelled = bool(self._cancel_callback())

        if cancelled:
            self._interrupted = True
            self._last_event = event

        return cancelled

    def reset(self) -> None:
        self._interrupted = False
        self._last_event = None
