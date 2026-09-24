import pytest

from sparks.router.model.cloud import CloudProvider
from sparks.router.model.provider import InferenceRequest
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)


def make_request() -> InferenceRequest:
    model = ModelDefinition(
        name="cloud-model",
        provider=ModelProvider.OPENAI,
        capability=ModelCapability.REASONING,
        context_window=32768,
    )

    return InferenceRequest(
        model=model,
        prompt="analyze this",
    )


def test_cloud_provider_is_disabled_by_default():
    provider = CloudProvider()

    assert provider.is_available() is False


def test_disabled_cloud_provider_fails_explicitly():
    provider = CloudProvider()

    with pytest.raises(RuntimeError, match="not configured"):
        provider.generate(make_request())