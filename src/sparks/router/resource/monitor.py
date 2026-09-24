from sparks.router.resource.gpu import GPUMonitor
from sparks.router.resource.snapshot import ResourceSnapshot


class ResourceMonitor:
    """
    Collects the current CPU, RAM, GPU and VRAM state.
    """

    def __init__(self) -> None:
        self.gpu_monitor = GPUMonitor()

    def snapshot(self) -> ResourceSnapshot:
        import psutil

        memory = psutil.virtual_memory()
        gpu = self.gpu_monitor.snapshot()

        return ResourceSnapshot(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            gpu_available=gpu.available,
            gpu_name=gpu.name,
            total_vram_mb=gpu.total_vram_mb,
            free_vram_mb=gpu.free_vram_mb,
            used_vram_mb=gpu.used_vram_mb,
        )
