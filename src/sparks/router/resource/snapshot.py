from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSnapshot:
    """
    Point-in-time machine resource state used by SPARKS.
    """

    cpu_percent: float
    memory_percent: float

    gpu_available: bool
    gpu_name: str | None
    total_vram_mb: int
    free_vram_mb: int
    used_vram_mb: int

    @property
    def memory_available(self) -> bool:
        return self.memory_percent < 85.0

    @property
    def gpu_available_for_inference(self) -> bool:
        return self.gpu_available and self.free_vram_mb > 0
