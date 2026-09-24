from sparks.router.model.catalog import OllamaCatalog
from sparks.router.model.mapping import ModelMapper
from sparks.router.model.registry import ModelRegistry


class ModelBootstrap:
    """
    Discovers installed provider models and registers them
    in the SPARKS model registry.
    """

    def __init__(
        self,
        catalog: OllamaCatalog | None = None,
        mapper: ModelMapper | None = None,
    ) -> None:
        self.catalog = catalog or OllamaCatalog()
        self.mapper = mapper or ModelMapper()

    def load_registry(self) -> ModelRegistry:
        registry = ModelRegistry()

        installed_models = self.catalog.list_models()

        for installed_model in installed_models:
            model = self.mapper.map(installed_model)
            registry.register(model)

        return registry