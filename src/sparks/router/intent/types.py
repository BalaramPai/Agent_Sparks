from enum import Enum


class IntentRoute(str, Enum):
    DETERMINISTIC = "deterministic"
    LOCAL_FAST = "local_fast"
    LOCAL_REASONING = "local_reasoning"
    CLOUD = "cloud"


class IntentResult:
    def __init__(
        self,
        route: IntentRoute,
        confidence: float,
        reason: str,
    ) -> None:
        self.route = route
        self.confidence = confidence
        self.reason = reason

    def __repr__(self) -> str:
        return (
            f"IntentResult("
            f"route={self.route.value!r}, "
            f"confidence={self.confidence:.2f}, "
            f"reason={self.reason!r})"
        )