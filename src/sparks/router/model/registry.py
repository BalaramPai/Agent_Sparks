from sparks.router.model.types import ModelCapability, ModelDefinition


class ModelRegistry:
    """
    Catalog of models available to the SPARKS runtime.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelDefinition] = {}

    def register(self, model: ModelDefinition) -> None:
        self._models[model.name] = model

    def get(self, name: str) -> ModelDefinition | None:
        return self._models.get(name)

    def find_by_capability(
        self,
        capability: ModelCapability,
    ) -> list[ModelDefinition]:
        return [
            model
            for model in self._models.values()
            if model.capability == capability
        ]

    def remove(self, name: str) -> None:
        self._models.pop(name, None)

    @property
    def models(self) -> list[ModelDefinition]:
        return list(self._models.values())