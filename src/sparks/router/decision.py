from dataclasses import dataclass

from sparks.router.intent.types import IntentResult, IntentRoute
from sparks.router.resource.governor import ResourceLevel


@dataclass(frozen=True)
class RoutingDecision:
    route: IntentRoute
    reason: str
    resource_level: ResourceLevel


class RoutingPolicy:
    """
    Combines user intent with current resource conditions.

    This is policy only. Actual model execution comes later.
    """

    def decide(
        self,
        intent: IntentResult,
        resource_level: ResourceLevel,
    ) -> RoutingDecision:

        # Deterministic actions should remain deterministic.
        if intent.route == IntentRoute.DETERMINISTIC:
            return RoutingDecision(
                route=IntentRoute.DETERMINISTIC,
                reason="deterministic action does not require model inference",
                resource_level=resource_level,
            )

        # Critical resource pressure means avoid expensive local inference.
        if resource_level == ResourceLevel.CRITICAL:
            return RoutingDecision(
                route=IntentRoute.CLOUD,
                reason="critical local resource pressure",
                resource_level=resource_level,
            )

        # Constrained resources prevent expensive local reasoning.
        if (
            resource_level == ResourceLevel.CONSTRAINED
            and intent.route == IntentRoute.LOCAL_REASONING
        ):
            return RoutingDecision(
                route=IntentRoute.CLOUD,
                reason="local reasoning deferred under resource pressure",
                resource_level=resource_level,
            )

        return RoutingDecision(
            route=intent.route,
            reason="intent route is compatible with current resources",
            resource_level=resource_level,
        )