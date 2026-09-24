from sparks.router.intent.types import IntentRoute
from sparks.router.router import IntentRouter


def test_router_routes_deterministic_request():
    router = IntentRouter()

    result = router.route("open vscode")

    assert result.route == IntentRoute.DETERMINISTIC


def test_router_routes_reasoning_request():
    router = IntentRouter()

    result = router.route("analyze this architecture")

    assert result.route == IntentRoute.LOCAL_REASONING


def test_router_returns_intent_result():
    router = IntentRouter()

    result = router.route("hello")

    assert result.confidence >= 0.0
    assert result.reason