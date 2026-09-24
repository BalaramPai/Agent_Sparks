from abc import ABC, abstractmethod
from dataclasses import dataclass

from sparks.router.model.types import ModelDefinition


@dataclass(frozen=True)
class InferenceRequest:
    """
    Input passed to a model provider.
    """

    model: ModelDefinition
    prompt: str
    system_prompt: str | None = None
    temperature: float = 0.2
    max_tokens: int = 1024


@dataclass(frozen=True)
class InferenceResult:
    """
    Standardized result returned by a model provider.
    """

    text: str
    model_name: str
    provider: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ModelProviderInterface(ABC):
    """
    Contract that every SPARKS model provider must implement.
    """

    @abstractmethod
    def generate(self, request: InferenceRequest) -> InferenceResult:
        """
        Execute inference for a request.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return whether the provider is currently available.
        """
        raise NotImplementedError