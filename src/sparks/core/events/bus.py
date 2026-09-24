from collections import defaultdict
from collections.abc import Callable
from typing import Any


EventHandler = Callable[[Any], None]


class EventBus:
    """
    Lightweight in-process event bus for SPARKS.

    Components can publish events without knowing
    which other components consume them.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a previously registered handler."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish an event to all registered handlers."""
        for handler in self._handlers[event_type]:
            handler(data)

    def clear(self) -> None:
        """Remove all registered handlers."""
        self._handlers.clear()

    @property
    def event_types(self) -> list[str]:
        """Return currently registered event types."""
        return list(self._handlers.keys())