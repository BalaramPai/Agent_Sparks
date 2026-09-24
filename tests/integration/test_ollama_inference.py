import pytest

from sparks.router.decision import RoutingPolicy
from sparks.router.inference import InferenceEngine
from sparks.router.model.bootstrap import ModelBootstrap
from sparks.router.model.manager import ModelManager
from sparks.router.model.ollama import OllamaProvider
from sparks.router.model.selector import ModelSelector
from sparks.router.resource.governor import ResourceGovernor
from sparks.router.resource.monitor import ResourceMonitor
from sparks.router.router import IntentRouter


def test_real_ollama_inference():
    provider = OllamaProvider()

    if not provider.is_available():
        pytest.skip("Ollama is not running")

    registry = ModelBootstrap().load_registry()

    model = registry.get("llama3.1:8b")

    if model is None:
        pytest.skip("llama3.1:8b is not installed")

    manager = ModelManager()
    manager.register(model, provider)
    manager.load(model.name)

    engine = InferenceEngine(
        router=IntentRouter(),
        resource_monitor=ResourceMonitor(),
        resource_governor=ResourceGovernor(),
        routing_policy=RoutingPolicy(),
        model_selector=ModelSelector(registry),
        model_manager=manager,
    )

    decision = engine.generate(
        "Reply with exactly: SPARKS ONLINE"
    )

    assert decision.result.text.strip()
    assert decision.result.model_name == "llama3.1:8b"