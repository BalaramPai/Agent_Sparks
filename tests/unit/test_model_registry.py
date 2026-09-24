from sparks.router.model.registry import ModelRegistry
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)


def test_register_and_get_model():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="fast-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
    )

    registry.register(model)

    assert registry.get("fast-local") == model


def test_find_models_by_capability():
    registry = ModelRegistry()

    fast = ModelDefinition(
        name="fast-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
    )

    reasoning = ModelDefinition(
        name="reasoning-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.REASONING,
        context_window=32768,
        requires_gpu=True,
        minimum_vram_mb=3000,
    )

    registry.register(fast)
    registry.register(reasoning)

    results = registry.find_by_capability(ModelCapability.REASONING)

    assert results == [reasoning]


def test_remove_model():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="fast-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
    )

    registry.register(model)
    registry.remove("fast-local")

    assert registry.get("fast-local") is None