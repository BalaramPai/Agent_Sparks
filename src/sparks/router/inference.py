from dataclasses import dataclass

from sparks.router.decision import RoutingPolicy
from sparks.router.intent.types import IntentRoute
from sparks.router.model.errors import (
    InferenceFailedError,
    ModelUnavailableError,
    NoCompatibleModelError,
)
from sparks.router.model.manager import ModelManager
from sparks.router.model.provider import InferenceRequest, InferenceResult
from sparks.router.model.selector import ModelSelector
from sparks.router.model.types import ModelCapability
from sparks.router.resource.governor import ResourceGovernor
from sparks.router.resource.monitor import ResourceMonitor
from sparks.router.router import IntentRouter


@dataclass(frozen=True)
class InferenceDecision:
    result: InferenceResult
    route: IntentRoute


class InferenceEngine:
    """
    Coordinates SPARKS intent routing, resource evaluation,
    model selection and inference.
    """

    def __init__(
        self,
        router: IntentRouter,
        resource_monitor: ResourceMonitor,
        resource_governor: ResourceGovernor,
        routing_policy: RoutingPolicy,
        model_selector: ModelSelector,
        model_manager: ModelManager,
    ) -> None:
        self.router = router
        self.resource_monitor = resource_monitor
        self.resource_governor = resource_governor
        self.routing_policy = routing_policy
        self.model_selector = model_selector
        self.model_manager = model_manager

    def generate(self, prompt: str) -> InferenceDecision:
        intent = self.router.route(prompt)

        resources = self.resource_monitor.snapshot()

        resource_level = self.resource_governor.evaluate(resources)

        decision = self.routing_policy.decide(
            intent,
            resource_level,
        )

        if decision.route == IntentRoute.DETERMINISTIC:
            raise NoCompatibleModelError(
                "Deterministic requests must be handled by the tool system"
            )

        if decision.route == IntentRoute.CLOUD:
            raise ModelUnavailableError(
                "Cloud inference provider is not implemented yet"
            )

        capability = self._capability_for_route(decision.route)

        warm_models = self._get_warm_models()

        if warm_models:
            model = self.model_selector.select(
                capability,
                resources,
                warm_models=warm_models,
            )
        else:
            model = self.model_selector.select(
                capability,
                resources,
            )
        if model is None:
            raise NoCompatibleModelError(
                f"No compatible local model for capability "
                f"'{capability.value}'"
            )

        request = InferenceRequest(
            model=model,
            prompt=prompt,
        )

        try:
            result = self.model_manager.generate(request)
        except RuntimeError as error:
            raise InferenceFailedError(
                f"Inference failed for model '{model.name}'"
            ) from error

        return InferenceDecision(
            result=result,
            route=decision.route,
        )

    def _get_warm_models(self) -> set[str]:
        loaded_models = getattr(self.model_manager, "loaded_models", None)

        if not isinstance(loaded_models, (list, tuple, set)):
            return set()

        return {
            state.model.name
            for state in loaded_models
            if state.loaded
        }
    @staticmethod
    def _capability_for_route(
        route: IntentRoute,
    ) -> ModelCapability:
        if route == IntentRoute.LOCAL_REASONING:
            return ModelCapability.REASONING

        return ModelCapability.GENERAL



