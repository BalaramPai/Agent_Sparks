from sparks.router.model.catalog import InstalledModel
from sparks.router.model.mapping import ModelMapper
from sparks.router.model.types import (
    ModelCapability,
    ModelProvider,
)


def test_8b_model_is_mapped_to_general_capability():
    mapper = ModelMapper()

    installed = InstalledModel(
        name="llama3.1:8b",
        provider=ModelProvider.OLLAMA,
    )

    model = mapper.map(installed)

    assert model.name == "llama3.1:8b"
    assert model.provider == ModelProvider.OLLAMA
    assert model.capability == ModelCapability.GENERAL
    assert model.requires_gpu is True
    assert model.minimum_vram_mb == 3000


def test_unknown_model_gets_safe_default():
    mapper = ModelMapper()

    installed = InstalledModel(
        name="unknown-model",
        provider=ModelProvider.OLLAMA,
    )

    model = mapper.map(installed)

    assert model.name == "unknown-model"
    assert model.capability == ModelCapability.GENERAL
    assert model.requires_gpu is False
