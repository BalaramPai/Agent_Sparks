from unittest.mock import Mock, patch

from sparks.router.model.catalog import OllamaCatalog, InstalledModel
from sparks.router.model.types import ModelProvider


def test_ollama_catalog_discovers_models():
    catalog = OllamaCatalog()

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3.2:3b"},
            {"name": "qwen2.5:7b"},
        ]
    }

    with patch(
        "sparks.router.model.catalog.httpx.get",
        return_value=mock_response,
    ):
        models = catalog.list_models()

    assert models == [
        InstalledModel(
            name="llama3.2:3b",
            provider=ModelProvider.OLLAMA,
        ),
        InstalledModel(
            name="qwen2.5:7b",
            provider=ModelProvider.OLLAMA,
        ),
    ]


def test_empty_ollama_catalog():
    catalog = OllamaCatalog()

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"models": []}

    with patch(
        "sparks.router.model.catalog.httpx.get",
        return_value=mock_response,
    ):
        models = catalog.list_models()

    assert models == []