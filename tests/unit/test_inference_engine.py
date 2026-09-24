from unittest.mock import Mock

from sparks.router.decision import RoutingPolicy
from sparks.router.inference import InferenceEngine
from sparks.router.intent.types import IntentResult, IntentRoute
from sparks.router.model.manager import ModelManager
from sparks.router.model.provider import InferenceResult
from sparks.router.model.selector import ModelSelector
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)
from sparks.router.resource.governor import ResourceGovernor
from sparks.router.resource.monitor import ResourceMonitor
from sparks.router.router import IntentRouter


def test_inference_engine_runs_local_request():
    router = Mock(spec=IntentRouter)

    router.route.return_value = IntentResult(
        route=IntentRoute.LOCAL_FAST,
        confidence=0.9,
        reason="simple request",
    )

    monitor = Mock(spec=ResourceMonitor)

    resources = Mock()
    resources.cpu_percent = 30.0
    resources.memory_percent = 50.0
    resources.gpu_available = True
    resources.free_vram_mb = 3500

    monitor.snapshot.return_value = resources

    model = ModelDefinition(
        name="llama3.1:8b",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.GENERAL,
        context_window=8192,
        requires_gpu=True,
        minimum_vram_mb=3500,
    )

    selector = Mock(spec=ModelSelector)
    selector.select.return_value = model

    manager = Mock(spec=ModelManager)
    manager.generate.return_value = InferenceResult(
        text="Hello from SPARKS",
        model_name="llama3.1:8b",
        provider="ollama",
    )

    engine = InferenceEngine(
        router=router,
        resource_monitor=monitor,
        resource_governor=ResourceGovernor(),
        routing_policy=RoutingPolicy(),
        model_selector=selector,
        model_manager=manager,
    )

    decision = engine.generate("hello")

    assert decision.route == IntentRoute.LOCAL_FAST
    assert decision.result.text == "Hello from SPARKS"

    selector.select.assert_called_once_with(
        ModelCapability.GENERAL,
        resources,
    )

    manager.generate.assert_called_once()