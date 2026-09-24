from sparks.router.decision import RoutingPolicy
from sparks.router.intent.types import IntentResult, IntentRoute
from sparks.router.resource.governor import ResourceLevel


def test_deterministic_action_ignores_resource_pressure():
    policy = RoutingPolicy()

    intent = IntentResult(
        route=IntentRoute.DETERMINISTIC,
        confidence=0.95,
        reason="system action",
    )

    decision = policy.decide(
        intent,
        ResourceLevel.CRITICAL,
    )

    assert decision.route == IntentRoute.DETERMINISTIC


def test_reasoning_moves_to_cloud_under_constrained_resources():
    policy = RoutingPolicy()

    intent = IntentResult(
        route=IntentRoute.LOCAL_REASONING,
        confidence=0.80,
        reason="complex analysis",
    )

    decision = policy.decide(
        intent,
        ResourceLevel.CONSTRAINED,
    )

    assert decision.route == IntentRoute.CLOUD


def test_reasoning_moves_to_cloud_under_critical_resources():
    policy = RoutingPolicy()

    intent = IntentResult(
        route=IntentRoute.LOCAL_REASONING,
        confidence=0.80,
        reason="complex analysis",
    )

    decision = policy.decide(
        intent,
        ResourceLevel.CRITICAL,
    )

    assert decision.route == IntentRoute.CLOUD


def test_local_fast_remains_local_when_resources_are_normal():
    policy = RoutingPolicy()

    intent = IntentResult(
        route=IntentRoute.LOCAL_FAST,
        confidence=0.80,
        reason="simple request",
    )

    decision = policy.decide(
        intent,
        ResourceLevel.NORMAL,
    )

    assert decision.route == IntentRoute.LOCAL_FAST