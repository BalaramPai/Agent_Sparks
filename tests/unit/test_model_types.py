from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)


def test_model_definition():
    model = ModelDefinition(
        name="fast-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
    )

    assert model.name == "fast-local"
    assert model.provider == ModelProvider.OLLAMA
    assert model.capability == ModelCapability.FAST


def test_gpu_model_definition():
    model = ModelDefinition(
        name="reasoning-local",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.REASONING,
        context_window=32768,
        requires_gpu=True,
        minimum_vram_mb=3000,
    )

    assert model.requires_gpu is True
    assert model.minimum_vram_mb == 3000