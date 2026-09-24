from unittest.mock import Mock, patch

from sparks.router.model.ollama import OllamaProvider
from sparks.router.model.provider import InferenceRequest
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)


def make_request() -> InferenceRequest:
    model = ModelDefinition(
        name="test-model",
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
    )

    return InferenceRequest(
        model=model,
        prompt="hello",
    )


def test_ollama_provider_generates_result():
    provider = OllamaProvider()

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "response": "Hello from Ollama",
        "prompt_eval_count": 5,
        "eval_count": 3,
    }

    with patch(
        "sparks.router.model.ollama.httpx.post",
        return_value=mock_response,
    ):
        result = provider.generate(make_request())

    assert result.text == "Hello from Ollama"
    assert result.model_name == "test-model"
    assert result.provider == "ollama"
    assert result.input_tokens == 5
    assert result.output_tokens == 3


def test_ollama_provider_availability():
    provider = OllamaProvider()

    mock_response = Mock()
    mock_response.is_success = True

    with patch(
        "sparks.router.model.ollama.httpx.get",
        return_value=mock_response,
    ):
        assert provider.is_available() is True