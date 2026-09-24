from sparks.router.model.registry import ModelRegistry
from sparks.router.model.selector import ModelSelector
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)
from sparks.router.resource.snapshot import ResourceSnapshot


def test_warm_model_can_be_selected_with_low_free_vram():
    registry = ModelRegistry()

    model = ModelDefinition(
        name="llama3.1:8b",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.GENERAL,
        context_window=8192,
        requires_gpu=True,
        minimum_vram_mb=3000,
    )

    registry.register(model)

    resources = ResourceSnapshot(
        cpu_percent=15.0,
        memory_percent=66.0,
        gpu_available=True,
        gpu_name="RTX 2050",
        total_vram_mb=4096,
        free_vram_mb=1293,
        used_vram_mb=2803,
    )

    selector = ModelSelector(registry)

    result = selector.select(
        ModelCapability.GENERAL,
        resources,
        warm_models={"llama3.1:8b"},
    )

    assert result == model