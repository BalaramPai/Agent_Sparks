from dataclasses import dataclass

from sparks.router.model.provider import (
    InferenceRequest,
    InferenceResult,
    ModelProviderInterface,
)
from sparks.router.model.types import ModelDefinition


@dataclass
class ModelRuntimeState:
    """
    Runtime state of a model.
    """

    model: ModelDefinition
    loaded: bool = False
    active: bool = False


class ModelManager:
    """
    Tracks model residency and delegates inference
    to the appropriate provider.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelRuntimeState] = {}
        self._providers: dict[str, ModelProviderInterface] = {}

    def register(
        self,
        model: ModelDefinition,
        provider: ModelProviderInterface,
    ) -> None:
        self._models[model.name] = ModelRuntimeState(model=model)
        self._providers[model.name] = provider

    def load(self, name: str) -> None:
        state = self._require(name)
        state.loaded = True

    def unload(self, name: str) -> None:
        state = self._require(name)
        state.loaded = False
        state.active = False

    def activate(self, name: str) -> None:
        state = self._require(name)

        if not state.loaded:
            raise RuntimeError(
                f"Model '{name}' must be loaded before activation"
            )

        for other in self._models.values():
            other.active = False

        state.active = True

    def generate(
        self,
        request: InferenceRequest,
    ) -> InferenceResult:
        state = self._require(request.model.name)

        if not state.loaded:
            raise RuntimeError(
                f"Model '{request.model.name}' is not loaded"
            )

        if not state.active:
            self.activate(request.model.name)

        provider = self._providers[request.model.name]

        if not provider.is_available():
            raise RuntimeError(
                f"Provider for '{request.model.name}' is unavailable"
            )

        return provider.generate(request)

    def get(self, name: str) -> ModelRuntimeState | None:
        return self._models.get(name)

    @property
    def active_model(self) -> ModelRuntimeState | None:
        for state in self._models.values():
            if state.active:
                return state

        return None

    @property
    def loaded_models(self) -> list[ModelRuntimeState]:
        return [
            state
            for state in self._models.values()
            if state.loaded
        ]

    def _require(self, name: str) -> ModelRuntimeState:
        state = self._models.get(name)

        if state is None:
            raise KeyError(f"Unknown model: {name}")

        return state
