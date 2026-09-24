from sparks.router.intent.detector import IntentDetector
from sparks.router.intent.types import IntentRoute


def test_system_action_is_deterministic():
    detector = IntentDetector()

    result = detector.detect("mute the computer")

    assert result.route == IntentRoute.DETERMINISTIC


def test_visual_request_uses_local_fast_path():
    detector = IntentDetector()

    result = detector.detect("what am I looking at")

    assert result.route == IntentRoute.LOCAL_FAST


def test_reasoning_request_uses_reasoning_path():
    detector = IntentDetector()

    result = detector.detect("analyze this architecture")

    assert result.route == IntentRoute.LOCAL_REASONING


def test_unknown_request_defaults_to_local_fast():
    detector = IntentDetector()

    result = detector.detect("tell me something interesting")

    assert result.route == IntentRoute.LOCAL_FAST