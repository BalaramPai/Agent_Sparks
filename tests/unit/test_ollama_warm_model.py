from unittest.mock import Mock, patch

from sparks.router.model.ollama import OllamaProvider


def test_ollama_detects_warm_model():
    provider = OllamaProvider()

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "models": [
            {"name": "llama3.1:8b"},
        ]
    }

    with patch(
        "sparks.router.model.ollama.httpx.get",
        return_value=response,
    ):
        assert provider.is_model_warm("llama3.1:8b") is True


def test_ollama_detects_cold_model():
    provider = OllamaProvider()

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "models": [
            {"name": "llama3.1:8b"},
        ]
    }

    with patch(
        "sparks.router.model.ollama.httpx.get",
        return_value=response,
    ):
        assert provider.is_model_warm("qwen:7b") is False