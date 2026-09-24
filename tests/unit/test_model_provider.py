from sparks.router.model.provider import (
    InferenceRequest,
    InferenceResult,
    ModelProviderInterface,
)
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)


class FakeProvider(ModelProviderInterface):
    def __init__(self, available: bool = True) -> None:
        self.available = available

    def generate(
        self,
        request: InferenceRequest,
    ) -> InferenceResult:
        return InferenceResult(
            text=f"response to: {request.prompt}",
            model_name=request.model.name,
            provider=request.model.provider.value,
        )

    def is_available(self) -> bool:
        return self.available


def make_model() -> ModelDefinition:
    return ModelDefinition(
        name="test-model",
        provider=ModelProvider.LOCAL,
        capability=ModelCapability.FAST,
        context_window=8192,
    )


def test_inference_request():
    request = InferenceRequest(
        model=make_model(),
        prompt="hello",
    )

    assert request.prompt == "hello"
    assert request.model.name == "test-model"


def test_provider_availability():
    provider = FakeProvider()

    assert provider.is_available() is True


def test_provider_generates_standardized_result():
    provider = FakeProvider()

    result = provider.generate(
        InferenceRequest(
            model=make_model(),
            prompt="hello",
        )
    )

    assert isinstance(result, InferenceResult)
    assert result.text == "response to: hello"
    assert result.model_name == "test-model"
    assert result.provider == "local"