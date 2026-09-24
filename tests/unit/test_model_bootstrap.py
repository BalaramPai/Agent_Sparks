from unittest.mock import Mock

from sparks.router.model.bootstrap import ModelBootstrap
from sparks.router.model.catalog import InstalledModel
from sparks.router.model.types import ModelProvider


def test_bootstrap_builds_registry():
    catalog = Mock()

    catalog.list_models.return_value = [
        InstalledModel(
            name="llama3.1:8b",
            provider=ModelProvider.OLLAMA,
        )
    ]

    bootstrap = ModelBootstrap(catalog=catalog)

    registry = bootstrap.load_registry()

    model = registry.get("llama3.1:8b")

    assert model is not None
    assert model.name == "llama3.1:8b"
    assert model.provider == ModelProvider.OLLAMA