from enum import Enum

from sparks.router.resource.snapshot import ResourceSnapshot


class ResourceLevel(str, Enum):
    NORMAL = "normal"
    CONSTRAINED = "constrained"
    CRITICAL = "critical"


class ResourceGovernor:
    """
    Converts raw machine resources into a runtime resource level.

    The governor does not decide what the user wants.
    It decides how much computation SPARKS should safely use.
    """

    def evaluate(self, snapshot: ResourceSnapshot) -> ResourceLevel:
        if snapshot.memory_percent >= 95.0:
            return ResourceLevel.CRITICAL

        if snapshot.cpu_percent >= 90.0:
            return ResourceLevel.CRITICAL

        if snapshot.gpu_available and snapshot.free_vram_mb < 512:
            return ResourceLevel.CRITICAL

        if snapshot.memory_percent >= 80.0:
            return ResourceLevel.CONSTRAINED

        if snapshot.cpu_percent >= 75.0:
            return ResourceLevel.CONSTRAINED

        if snapshot.gpu_available and snapshot.free_vram_mb < 1024:
            return ResourceLevel.CONSTRAINED

        return ResourceLevel.NORMAL