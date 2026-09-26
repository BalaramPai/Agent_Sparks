from __future__ import annotations

from threading import Event


class CancellationError(Exception):
    """Raised when an operation is cancelled."""


class CancellationToken:
    """
    Cooperative cancellation token for a single operation.

    Cancellation is explicit and thread-safe.
    """

    def __init__(self) -> None:
        self._event = Event()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()

    def throw_if_cancelled(self) -> None:
        if self.is_cancelled:
            raise CancellationError("Operation cancelled")
