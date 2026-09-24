from sparks.router.model.catalog import InstalledModel
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
)


class ModelMapper:
    """
    Maps provider-specific installed models to SPARKS model definitions.
    """

    def map(self, model: InstalledModel) -> ModelDefinition:
        name = model.name.lower()

        if "8b" in name:
            return ModelDefinition(
                name=model.name,
                provider=model.provider,
                capability=ModelCapability.GENERAL,
                context_window=8192,
                requires_gpu=True,
                minimum_vram_mb=3000,
                priority=20,
            )

        return ModelDefinition(
            name=model.name,
            provider=model.provider,
            capability=ModelCapability.GENERAL,
            context_window=8192,
            requires_gpu=False,
            minimum_vram_mb=0,
            priority=100,
        )
