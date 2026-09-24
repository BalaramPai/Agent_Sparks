from sparks.router.intent.detector import IntentDetector
from sparks.router.intent.types import IntentResult


class IntentRouter:
    """
    Coordinates intent detection and produces the initial
    computation route for a user request.

    Model execution is intentionally not handled here yet.
    """

    def __init__(self) -> None:
        self.detector = IntentDetector()

    def route(self, text: str) -> IntentResult:
        """
        Determine the appropriate computation route.

        The router currently delegates to deterministic intent
        detection. Resource-aware routing will be added later.
        """
        return self.detector.detect(text)