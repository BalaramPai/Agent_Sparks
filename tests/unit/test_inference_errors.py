from unittest.mock import Mock

import pytest

from sparks.router.decision import RoutingPolicy
from sparks.router.inference import InferenceEngine
from sparks.router.intent.types import IntentResult, IntentRoute
from sparks.router.model.errors import (
    InferenceFailedError,
    NoCompatibleModelError,
)
from sparks.router.model.manager import ModelManager
from sparks.router.model.selector import ModelSelector
from sparks.router.resource.governor import ResourceGovernor
from sparks.router.resource.monitor import ResourceMonitor


def make_engine(
    route: IntentRoute,
    model=None,
    generate_error=None,
):
    router = Mock()
    router.route.return_value = IntentResult(
        route=route,
        confidence=0.9,
        reason="test",
    )

    monitor = Mock(spec=ResourceMonitor)

    resources = Mock()
    resources.cpu_percent = 20.0
    resources.memory_percent = 40.0
    resources.gpu_available = True
    resources.free_vram_mb = 4000

    monitor.snapshot.return_value = resources

    selector = Mock(spec=ModelSelector)
    selector.select.return_value = model

    manager = Mock(spec=ModelManager)

    if generate_error:
        manager.generate.side_effect = generate_error

    return InferenceEngine(
        router=router,
        resource_monitor=monitor,
        resource_governor=ResourceGovernor(),
        routing_policy=RoutingPolicy(),
        model_selector=selector,
        model_manager=manager,
    )


def test_missing_model_is_controlled_failure():
    engine = make_engine(
        IntentRoute.LOCAL_FAST,
        model=None,
    )

    with pytest.raises(NoCompatibleModelError):
        engine.generate("hello")


def test_provider_failure_becomes_inference_error():
    from sparks.router.model.types import (
        ModelCapability,
        ModelDefinition,
        ModelProvider,
    )

    model = ModelDefinition(
        name="test-model",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.GENERAL,
        context_window=8192,
    )

    engine = make_engine(
        IntentRoute.LOCAL_FAST,
        model=model,
        generate_error=RuntimeError("provider failed"),
    )

    with pytest.raises(InferenceFailedError):
        engine.generate("hello")
