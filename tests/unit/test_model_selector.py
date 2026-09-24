from sparks.router.model.registry import ModelRegistry
from sparks.router.model.selector import ModelSelector
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)
from sparks.router.resource.snapshot import ResourceSnapshot


def make_resources(
    gpu: bool = True,
    free_vram: int = 4096,
) -> ResourceSnapshot:
    return ResourceSnapshot(
        cpu_percent=30.0,
        memory_percent=50.0,
        gpu_available=gpu,
        gpu_name="RTX 2050" if gpu else None,
        total_vram_mb=4096 if gpu else 0,
        free_vram_mb=free_vram,
        used_vram_mb=4096 - free_vram if gpu else 0,
    )


def test_selector_returns_compatible_model():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="reasoning-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.REASONING,
        context_window=32768,
        requires_gpu=True,
        minimum_vram_mb=3000,
    )

    registry.register(model)

    selector = ModelSelector(registry)

    result = selector.select(
        ModelCapability.REASONING,
        make_resources(free_vram=3500),
    )

    assert result == model


def test_selector_rejects_model_when_vram_is_insufficient():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="reasoning-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.REASONING,
        context_window=32768,
        requires_gpu=True,
        minimum_vram_mb=3000,
    )

    registry.register(model)

    selector = ModelSelector(registry)

    result = selector.select(
        ModelCapability.REASONING,
        make_resources(free_vram=2000),
    )

    assert result is None


def test_selector_rejects_gpu_model_without_gpu():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="reasoning-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.REASONING,
        context_window=32768,
        requires_gpu=True,
        minimum_vram_mb=3000,
    )

    registry.register(model)

    selector = ModelSelector(registry)

    result = selector.select(
        ModelCapability.REASONING,
        make_resources(gpu=False),
    )

    assert result is None


def test_cpu_model_does_not_require_gpu():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="fast-cpu",
        provider=ModelProvider.LOCAL,
        capability=ModelCapability.FAST,
        context_window=8192,
        requires_gpu=False,
    )

    registry.register(model)

    selector = ModelSelector(registry)

    result = selector.select(
        ModelCapability.FAST,
        make_resources(gpu=False),
    )

    assert result == model


def test_selector_prefers_lower_priority():
    registry = ModelRegistry()

    preferred = ModelDefinition(
        name="preferred-fast",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
        priority=10,
    )

    fallback = ModelDefinition(
        name="fallback-fast",
        provider=ModelProvider.LOCAL,
        capability=ModelCapability.FAST,
        context_window=8192,
        priority=50,
    )

    registry.register(fallback)
    registry.register(preferred)

    selector = ModelSelector(registry)

    result = selector.select(
        ModelCapability.FAST,
        make_resources(),
    )

    assert result == preferred
