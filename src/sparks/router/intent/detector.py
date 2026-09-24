from sparks.router.intent.types import IntentResult, IntentRoute


class IntentDetector:
    """
    Deterministic first-pass intent detector.

    This layer should be fast, predictable, and require no model inference.
    """

    _DETERMINISTIC_PATTERNS = {
        "open ",
        "close ",
        "launch ",
        "start ",
        "stop ",
        "mute",
        "unmute",
        "volume ",
        "brightness ",
        "lock computer",
        "shutdown",
        "restart",
        "sleep computer",
    }

    _VISION_PATTERNS = {
        "what am i looking at",
        "what is on my screen",
        "what's on my screen",
        "look at this",
        "what is this",
        "what's this",
        "describe this",
    }

    _REASONING_PATTERNS = {
        "analyze",
        "architecture",
        "design",
        "debug",
        "explain why",
        "compare",
        "plan",
        "reason",
        "complex",
    }

    def detect(self, text: str) -> IntentResult:
        """
        Detect the cheapest reliable route for a user request.
        """

        normalized = text.strip().lower()

        if not normalized:
            return IntentResult(
                route=IntentRoute.DETERMINISTIC,
                confidence=1.0,
                reason="empty input",
            )

        if self._matches(normalized, self._DETERMINISTIC_PATTERNS):
            return IntentResult(
                route=IntentRoute.DETERMINISTIC,
                confidence=0.95,
                reason="matched deterministic system action",
            )

        if self._matches(normalized, self._VISION_PATTERNS):
            return IntentResult(
                route=IntentRoute.LOCAL_FAST,
                confidence=0.90,
                reason="request requires visual context",
            )

        if self._matches(normalized, self._REASONING_PATTERNS):
            return IntentResult(
                route=IntentRoute.LOCAL_REASONING,
                confidence=0.75,
                reason="request indicates reasoning or analysis",
            )

        return IntentResult(
            route=IntentRoute.LOCAL_FAST,
            confidence=0.50,
            reason="no deterministic pattern matched",
        )

    @staticmethod
    def _matches(text: str, patterns: set[str]) -> bool:
        return any(pattern in text for pattern in patterns)