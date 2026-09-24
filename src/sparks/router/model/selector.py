from sparks.router.model.registry import ModelRegistry
from sparks.router.model.types import ModelCapability, ModelDefinition
from sparks.router.resource.snapshot import ResourceSnapshot


class ModelSelector:
    """
    Selects the most appropriate compatible model.

    Warm models are preferred because they do not require
    an additional cold-start residency decision.
    """

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def select(
        self,
        capability: ModelCapability,
        resources: ResourceSnapshot,
        warm_models: set[str] | None = None,
    ) -> ModelDefinition | None:
        candidates = self.registry.find_by_capability(capability)

        compatible = [
            model
            for model in candidates
            if self._is_compatible(
                model,
                resources,
                warm_models or set(),
            )
        ]

        if not compatible:
            return None

        return min(
            compatible,
            key=lambda model: (
                model.name not in (warm_models or set()),
                model.priority,
            ),
        )

    @staticmethod
    def _is_compatible(
        model: ModelDefinition,
        resources: ResourceSnapshot,
        warm_models: set[str],
    ) -> bool:
        if model.name in warm_models:
            return True

        if model.requires_gpu:
            if not resources.gpu_available:
                return False

            if resources.free_vram_mb < model.minimum_vram_mb:
                return False

        return True
